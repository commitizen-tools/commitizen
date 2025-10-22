from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TypedDict

import questionary

from commitizen import factory, git, out
from commitizen.config import BaseConfig
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


class CommitArgs(TypedDict, total=False):
    all: bool
    dry_run: bool
    edit: bool
    extra_cli_args: str
    message_length_limit: int
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
        self.encoding = config.settings["encoding"]
        self.cz = factory.committer_factory(self.config)
        self.arguments = arguments
        self.temp_file: str = get_backup_file_path()

    def _read_backup_message(self) -> str | None:
        # Check the commit backup file exists
        if not os.path.isfile(self.temp_file):
            return None

        # Read commit message from backup
        with open(self.temp_file, encoding=self.encoding) as f:
            return f.read().strip()

    def _prompt_commit_questions(self) -> str:
        # Prompt user for the commit message
        cz = self.cz
        questions = cz.questions()
        for question in (q for q in questions if q["type"] == "list"):
            question["use_shortcuts"] = self.config.settings["use_shortcuts"]
        try:
            answers = questionary.prompt(questions, style=cz.style)
        except ValueError as err:
            root_err = err.__context__
            if isinstance(root_err, CzException):
                raise CustomError(root_err.__str__())
            raise err

        if not answers:
            raise NoAnswersError()

        message = cz.message(answers)
        message_len = len(message.partition("\n")[0].strip())
        message_length_limit = self.arguments.get("message_length_limit", 0)
        if 0 < message_length_limit < message_len:
            raise CommitMessageLengthExceededError(
                f"Length of commit message exceeds limit ({message_len}/{message_length_limit})"
            )

        return message

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
            m = self._read_backup_message()
            if m is None:
                raise NoCommitBackupError()
            return m

        if self.config.settings.get("retry_after_failure") and not self.arguments.get(
            "no_retry"
        ):
            return self._read_backup_message() or self._prompt_commit_questions()
        return self._prompt_commit_questions()

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

        m = self._get_message()
        if self.arguments.get("edit"):
            m = self.manual_edit(m)

        out.info(f"\n{m}\n")

        if write_message_to_file:
            with smart_open(write_message_to_file, "w", encoding=self.encoding) as file:
                file.write(m)

        if dry_run:
            raise DryRunExit()

        if self.config.settings["always_signoff"] or signoff:
            extra_args = f"{extra_args} -s".strip()

        c = git.commit(m, args=extra_args)
        if c.return_code != 0:
            out.error(c.err)

            # Create commit backup
            with smart_open(self.temp_file, "w", encoding=self.encoding) as f:
                f.write(m)

            raise CommitError()

        if any(s in c.out for s in ("nothing added", "no changes added to commit")):
            out.error(c.out)
            return

        with contextlib.suppress(FileNotFoundError):
            os.remove(self.temp_file)
        out.write(c.err)
        out.write(c.out)
        out.success("Commit successful!")
