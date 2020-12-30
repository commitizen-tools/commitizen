import os
import re
import sys
from typing import Dict, Optional

from commitizen import factory, git, out
from commitizen.config import BaseConfig
from commitizen.exceptions import (
    InvalidCommandArgumentError,
    InvalidCommitMessageError,
    NoCommitsFoundError,
)


class Check:
    """Check if the current commit msg matches the commitizen format."""

    def __init__(self, config: BaseConfig, arguments: Dict[str, str], cwd=os.getcwd()):
        """Initial check command.

        Args:
            config: The config object required for the command to perform its action
            arguments: All the flags provided by the user
            cwd: Current work directory
        """
        self.commit_msg_file: Optional[str] = arguments.get("commit_msg_file")
        self.commit_msg: Optional[str] = arguments.get("message")
        self.rev_range: Optional[str] = arguments.get("rev_range")

        self._valid_command_argument()

        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

    def _valid_command_argument(self):
        number_args_provided = (
            bool(self.commit_msg_file) + bool(self.commit_msg) + bool(self.rev_range)
        )
        if number_args_provided == 0 and not os.isatty(0):
            self.commit_msg: Optional[str] = sys.stdin.read()
        elif number_args_provided != 1:
            raise InvalidCommandArgumentError(
                (
                    "One and only one argument is required for check command! "
                    "See 'cz check -h' for more information"
                )
            )

    def __call__(self):
        """Validate if commit messages follows the conventional pattern.

        Raises:
            InvalidCommitMessageError: if the commit provided not follows the conventional pattern
        """
        commits = self._get_commits()
        if not commits:
            raise NoCommitsFoundError(f"No commit found with range: '{self.rev_range}'")

        pattern = self.cz.schema_pattern()
        ill_formated_commits = [
            commit
            for commit in commits
            if not Check.validate_commit_message(commit.message, pattern)
        ]
        displayed_msgs_content = "\n".join(
            [
                f'commit "{commit.rev}": "{commit.message}"'
                for commit in ill_formated_commits
            ]
        )
        if displayed_msgs_content:
            raise InvalidCommitMessageError(
                "commit validation: failed!\n"
                "please enter a commit message in the commitizen format.\n"
                f"{displayed_msgs_content}\n"
                f"pattern: {pattern}"
            )
        out.success("Commit validation: successful!")

    def _get_commits(self):
        # Get commit message from file (--commit-msg-file)
        if self.commit_msg_file:
            with open(self.commit_msg_file, "r", encoding="utf-8") as commit_file:
                commit_title = commit_file.readline()
                commit_body = commit_file.read()
            return [git.GitCommit(rev="", title=commit_title, body=commit_body)]
        elif self.commit_msg:
            return [git.GitCommit(rev="", title="", body=self.commit_msg)]

        # Get commit messages from git log (--rev-range)
        return git.get_commits(end=self.rev_range)

    @staticmethod
    def validate_commit_message(commit_msg: str, pattern: str) -> bool:
        if commit_msg.startswith("Merge") or commit_msg.startswith("Revert"):
            return True
        return bool(re.match(pattern, commit_msg))
