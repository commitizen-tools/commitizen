from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING, TypedDict

import questionary

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

if TYPE_CHECKING:
    from pathlib import Path

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

    def __init__(self, config: BaseConfig, arguments: CommitArgs) -> None:
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.cz = factory.committer_factory(self.config)
        self.arguments = arguments
        self.backup_file_path = get_backup_file_path()

    def _read_backup_message(self) -> str | None:
        # Check the commit backup file exists
        if not self.backup_file_path.is_file():
            return None

        # Read commit message from backup
        with open(
            self.backup_file_path, encoding=self.config.settings["encoding"]
        ) as f:
            return f.read().strip()

    def _get_message_by_prompt_commit_questions(self) -> str:
        # Prompt user for the commit message
        questions = self.cz.questions()
        for question in (q for q in questions if q["type"] == "list"):
            question["use_shortcuts"] = self.config.settings["use_shortcuts"]
        try:
            answers = questionary.prompt(questions, style=self.cz.style)
        except ValueError as err:
            root_err = err.__context__
            if isinstance(root_err, CzException):
                raise CustomError(str(root_err))
            raise err

        if not answers:
            raise NoAnswersError()

        message = self.cz.message(answers)
        if limit := self.arguments.get(
            "message_length_limit", self.config.settings.get("message_length_limit", 0)
        ):
            self._validate_subject_length(message=message, length_limit=limit)

        return message

    def _validate_subject_length(self, *, message: str, length_limit: int) -> None:
        # By the contract, message_length_limit is set to 0 for no limit
        subject = message.partition("\n")[0].strip()
        if len(subject) > length_limit:
            raise CommitMessageLengthExceededError(
                f"Length of commit message exceeds limit ({len(subject)}/{length_limit}), subject: '{subject}'"
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
        with open(file_path) as temp_file:
            message = temp_file.read().strip()
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
