from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

import questionary
from prompt_toolkit.application.current import get_app

from commitizen import factory, git, out
from commitizen.cz.exceptions import CzException
from commitizen.cz.utils import get_backup_file_path
from commitizen.exceptions import (
    CommitError,
    CommitMessageLengthExceededError,
    CustomError,
    DryRunExit,
    NoAnswersError,
    NoCommitBackupError,
    NotAGitProjectError,
    NotAllowed,
    NothingToCommitError,
)
from commitizen.git import smart_open
from commitizen.interactive_preview import (
    make_length_validator as make_length_validator_preview,
)
from commitizen.interactive_preview import (
    make_toolbar_content as make_toolbar_content_preview,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from commitizen.config import BaseConfig


class CommitArgs(TypedDict, total=False):
    all: bool
    dry_run: bool
    edit: bool
    extra_cli_args: str
    message_length_limit: int | None
    no_retry: bool
    signoff: bool
    write_message_to_file: Path | None
    retry: bool


class Commit:
    """Show prompt for the user to create a guided commit."""

    # Questionary types for interactive preview hooks (length validator / toolbar),
    # based on questionary 2.0.1
    VALIDATABLE_TYPES = {"input", "text", "password", "path", "checkbox"}
    BOTTOM_TOOLBAR_TYPES = {"input", "text", "password", "confirm"}

    def __init__(self, config: BaseConfig, arguments: CommitArgs) -> None:
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.cz = factory.committer_factory(self.config)
        self.arguments = arguments
        self.backup_file_path = get_backup_file_path()

        message_length_limit = arguments.get("message_length_limit")
        self.message_length_limit: int = (
            message_length_limit
            if message_length_limit is not None
            else config.settings["message_length_limit"]
        )

    def _read_backup_message(self) -> str | None:
        # Check the commit backup file exists
        if not self.backup_file_path.is_file():
            return None

        # Read commit message from backup
        return self.backup_file_path.read_text(
            encoding=self.config.settings["encoding"]
        ).strip()

    def _build_commit_questions(
        self,
        questions: list,
        preview_enabled: bool,
        max_preview_length: int,
    ) -> list:
        """Build the list of questions to ask; add toolbar/validate when preview enabled."""
        if not preview_enabled:
            return list(questions)

        default_answers: dict[str, Any] = {
            q["name"]: q.get("default", "")
            for q in questions
            if isinstance(q.get("name"), str)
        }
        field_filters: dict[str, Any] = {
            q["name"]: q.get("filter")
            for q in questions
            if isinstance(q.get("name"), str)
        }
        answers_state: dict[str, Any] = {}

        def _get_current_buffer_text() -> str:
            try:
                app = get_app()
                buffer = app.layout.current_buffer
                return buffer.text if buffer is not None else ""
            except Exception:
                return ""

        def subject_builder(current_field: str, current_text: str) -> str:
            preview_answers: dict[str, Any] = default_answers.copy()
            preview_answers.update(answers_state)
            if current_field:
                field_filter = field_filters.get(current_field)
                if field_filter:
                    try:
                        preview_answers[current_field] = field_filter(current_text)
                    except Exception:
                        preview_answers[current_field] = current_text
                else:
                    preview_answers[current_field] = current_text
            try:
                return self.cz.message(preview_answers).partition("\n")[0].strip()
            except Exception:
                return ""

        def make_stateful_filter(
            name: str, original_filter: Callable[[str], Any] | None
        ) -> Callable[[str], Any]:
            def _filter(raw: str) -> Any:
                value = original_filter(raw) if original_filter else raw
                answers_state[name] = value
                return value

            return _filter

        def make_toolbar(name: str) -> Callable[[], str]:
            def _toolbar() -> str:
                return make_toolbar_content_preview(
                    subject_builder,
                    name,
                    _get_current_buffer_text(),
                    max_length=max_preview_length,
                )

            return _toolbar

        def make_length_validator(name: str) -> Callable[[str], bool | str]:
            return make_length_validator_preview(
                subject_builder,
                name,
                max_length=max_preview_length,
            )

        enhanced_questions: list[dict[str, object]] = []
        for q in questions:
            q_dict = dict(q)
            q_type = q_dict.get("type")
            name = q_dict.get("name")

            if isinstance(name, str):
                original_filter = q_dict.get("filter")
                q_dict["filter"] = make_stateful_filter(name, original_filter)

                if q_type in self.BOTTOM_TOOLBAR_TYPES:
                    q_dict["bottom_toolbar"] = make_toolbar(name)

                if q_type in self.VALIDATABLE_TYPES:
                    q_dict["validate"] = make_length_validator(name)

            enhanced_questions.append(q_dict)
        return enhanced_questions

    def _get_message_by_prompt_commit_questions(self) -> str:
        questions = self.cz.questions()
        for question in (q for q in questions if q["type"] == "list"):
            question["use_shortcuts"] = self.config.settings["use_shortcuts"]

        preview_enabled = bool(
            self.arguments.get("preview", False)
            or self.config.settings.get("preview", False)
        )
        max_preview_length = self.arguments.get(
            "message_length_limit",
            self.config.settings.get("message_length_limit", 0),
        )

        questions_to_ask = self._build_commit_questions(
            questions, preview_enabled, max_preview_length
        )

        try:
            answers = questionary.prompt(questions_to_ask, style=self.cz.style)
        except ValueError as err:
            root_err = err.__context__
            if isinstance(root_err, CzException):
                raise CustomError(str(root_err))
            raise err

        if not answers:
            raise NoAnswersError()

        message = self.cz.message(answers)
        self._validate_subject_length(message)
        return message

    def _validate_subject_length(self, message: str) -> None:
        # By the contract, message_length_limit is set to 0 for no limit
        if self.message_length_limit <= 0:
            return

        subject = message.partition("\n")[0].strip()
        if len(subject) > self.message_length_limit:
            raise CommitMessageLengthExceededError(
                f"Length of commit message exceeds limit ({len(subject)}/{self.message_length_limit}), subject: '{subject}'"
            )

    def manual_edit(self, message: str) -> str:
        editor = git.get_core_editor()
        if editor is None:
            raise RuntimeError("No 'editor' value given and no default available.")
        exec_path = shutil.which(editor)
        if exec_path is None:
            raise RuntimeError(f"Editor '{editor}' not found.")
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as file:
            file.write(message)
        file_path = file.name
        argv = [exec_path, file_path]
        subprocess.call(argv)
        message = Path(file_path).read_text().strip()
        os.unlink(file.name)
        return message

    def _get_message(self) -> str:
        if self.arguments.get("retry"):
            commit_message = self._read_backup_message()
            if commit_message is None:
                raise NoCommitBackupError()
            return commit_message

        if (
            self.config.settings.get("retry_after_failure")
            and not self.arguments.get("no_retry")
            and (backup_message := self._read_backup_message())
        ):
            return backup_message
        return self._get_message_by_prompt_commit_questions()

    def __call__(self) -> None:
        extra_args = self.arguments.get("extra_cli_args", "")
        dry_run = bool(self.arguments.get("dry_run"))
        write_message_to_file = self.arguments.get("write_message_to_file")
        signoff = bool(self.arguments.get("signoff"))

        if signoff:
            out.warn(
                "Deprecated warning: `cz commit -s` is deprecated and will be removed in v5, please use `cz commit -- -s` instead."
            )

        if self.arguments.get("all"):
            git.add("-u")

        if git.is_staging_clean() and not (dry_run or "--allow-empty" in extra_args):
            raise NothingToCommitError("No files added to staging!")

        if write_message_to_file is not None and write_message_to_file.is_dir():
            raise NotAllowed(f"{write_message_to_file} is a directory")

        commit_message = self._get_message()
        if self.arguments.get("edit"):
            commit_message = self.manual_edit(commit_message)

        out.info(f"\n{commit_message}\n")

        if write_message_to_file:
            with smart_open(
                write_message_to_file, "w", encoding=self.config.settings["encoding"]
            ) as file:
                file.write(commit_message)

        if dry_run:
            raise DryRunExit()

        if self.config.settings["always_signoff"] or signoff:
            extra_args = f"{extra_args} -s".strip()

        c = git.commit(commit_message, args=extra_args)
        if c.return_code != 0:
            out.error(c.err)

            # Create commit backup
            with smart_open(
                self.backup_file_path, "w", encoding=self.config.settings["encoding"]
            ) as f:
                f.write(commit_message)

            raise CommitError()

        if any(s in c.out for s in ("nothing added", "no changes added to commit")):
            out.error(c.out)
            return

        with contextlib.suppress(FileNotFoundError):
            self.backup_file_path.unlink()
        out.write(c.err)
        out.write(c.out)
        out.success("Commit successful!")
