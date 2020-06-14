import os
import re
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
        self.rev_range: Optional[str] = arguments.get("rev_range")

        self._valid_command_argument()

        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

    def _valid_command_argument(self):
        if bool(self.commit_msg_file) is bool(self.rev_range):
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
        commit_msgs = self._get_commit_messages()
        if not commit_msgs:
            raise NoCommitsFoundError(f"No commit found with range: '{self.rev_range}'")

        pattern = self.cz.schema_pattern()
        for commit_msg in commit_msgs:
            if not Check.validate_commit_message(commit_msg, pattern):
                raise InvalidCommitMessageError(
                    "commit validation: failed!\n"
                    "please enter a commit message in the commitizen format.\n"
                    f"commit: {commit_msg}\n"
                    f"pattern: {pattern}"
                )
        out.success("Commit validation: successful!")

    def _get_commit_messages(self):
        # Get commit message from file (--commit-msg-file)
        if self.commit_msg_file:
            with open(self.commit_msg_file, "r") as commit_file:
                commit_msg = commit_file.read()
            return [commit_msg]

        # Get commit messages from git log (--rev-range)
        return [commit.message for commit in git.get_commits(end=self.rev_range)]

    @staticmethod
    def validate_commit_message(commit_msg: str, pattern: str) -> bool:
        if commit_msg.startswith("Merge") or commit_msg.startswith("Revert"):
            return True
        return bool(re.match(pattern, commit_msg))
