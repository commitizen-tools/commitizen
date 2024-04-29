from __future__ import annotations

import contextlib
import os


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


class Commit:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: BaseConfig, arguments: dict):
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.encoding = config.settings["encoding"]
        self.cz = factory.commiter_factory(self.config)
        self.arguments = arguments
        self.temp_file: str = get_backup_file_path()

    def read_backup_message(self) -> str | None:
        # Check the commit backup file exists
        if not os.path.isfile(self.temp_file):
            return None

        # Read commit message from backup
        with open(self.temp_file, encoding=self.encoding) as f:
            return f.read().strip()

    def prompt_commit_questions(self) -> str:
        # Prompt user for the commit message
        cz = self.cz
        questions = cz.questions()
        for question in filter(lambda q: q["type"] == "list", questions):
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
        message_length_limit: int = self.arguments.get("message_length_limit", 0)
        if 0 < message_length_limit < message_len:
            raise CommitMessageLengthExceededError(
                f"Length of commit message exceeds limit ({message_len}/{message_length_limit})"
            )

        return message

    def __call__(self):
        dry_run: bool = self.arguments.get("dry_run")
        write_message_to_file: bool = self.arguments.get("write_message_to_file")

        is_all: bool = self.arguments.get("all")
        if is_all:
            c = git.add("-u")

        if git.is_staging_clean() and not dry_run:
            raise NothingToCommitError("No files added to staging!")

        if write_message_to_file is not None and write_message_to_file.is_dir():
            raise NotAllowed(f"{write_message_to_file} is a directory")

        retry: bool = self.arguments.get("retry")
        no_retry: bool = self.arguments.get("no_retry")
        retry_after_failure: bool = self.config.settings.get("retry_after_failure")

        if retry:
            m = self.read_backup_message()
            if m is None:
                raise NoCommitBackupError()
        elif retry_after_failure and not no_retry:
            m = self.read_backup_message()
            if m is None:
                m = self.prompt_commit_questions()
        else:
            m = self.prompt_commit_questions()

        out.info(f"\n{m}\n")

        if write_message_to_file:
            with smart_open(write_message_to_file, "w", encoding=self.encoding) as file:
                file.write(m)

        if dry_run:
            raise DryRunExit()

        signoff: bool = (
            self.arguments.get("signoff") or self.config.settings["always_signoff"]
        )

        if signoff:
            out.warn(
                "signoff mechanic is deprecated, please use `cz commit -- -s` instead."
            )
            extra_args = self.arguments.get("extra_cli_args", "--") + " -s"
        else:
            extra_args = self.arguments.get("extra_cli_args", "")

        c = git.commit(m, args=extra_args)

        if c.return_code != 0:
            out.error(c.err)

            # Create commit backup
            with smart_open(self.temp_file, "w", encoding=self.encoding) as f:
                f.write(m)

            raise CommitError()

        if "nothing added" in c.out or "no changes added to commit" in c.out:
            out.error(c.out)
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(self.temp_file)
            out.write(c.err)
            out.write(c.out)
            out.success("Commit successful!")
