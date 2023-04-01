import os
import sys
from typing import Any, Dict, Optional

from commitizen import factory, git, out
from commitizen.config import BaseConfig
from commitizen.exceptions import InvalidCommandArgumentError, NoCommitsFoundError


class Check:
    """Check if the current commit msg matches the commitizen format."""

    def __init__(self, config: BaseConfig, arguments: Dict[str, Any], cwd=os.getcwd()):
        """Initial check command.

        Args:
            config: The config object required for the command to perform its action
            arguments: All the flags provided by the user
            cwd: Current work directory
        """
        self.commit_msg_file: Optional[str] = arguments.get("commit_msg_file")
        self.commit_msg: Optional[str] = arguments.get("message")
        self.rev_range: Optional[str] = arguments.get("rev_range")
        self.allow_abort: bool = bool(
            arguments.get("allow_abort", config.settings["allow_abort"])
        )

        self._valid_command_argument()

        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

    def _valid_command_argument(self):
        num_exclusive_args_provided = sum(
            arg is not None
            for arg in (self.commit_msg_file, self.commit_msg, self.rev_range)
        )
        if num_exclusive_args_provided == 0 and not sys.stdin.isatty():
            self.commit_msg: Optional[str] = sys.stdin.read()
        elif num_exclusive_args_provided != 1:
            raise InvalidCommandArgumentError(
                (
                    "Only one of --rev-range, --message, and --commit-msg-file is permitted by check command! "
                    "See 'cz check -h' for more information"
                )
            )

    def __call__(self):
        """Validate if commit messages follows the conventional pattern.

        Raises:
            InvalidCommitMessageError: if the provided commit does not follow the conventional pattern
        """
        commits = self._get_commits()
        if not commits:
            raise NoCommitsFoundError(f"No commit found with range: '{self.rev_range}'")

        self.cz.validate_commits(commits, self.allow_abort)
        out.success("Commit validation: successful!")

    def _get_commits(self):
        msg = None
        # Get commit message from file (--commit-msg-file)
        if self.commit_msg_file is not None:
            # Enter this branch if commit_msg_file is "".
            with open(self.commit_msg_file, "r", encoding="utf-8") as commit_file:
                msg = commit_file.read()
        # Get commit message from command line (--message)
        elif self.commit_msg is not None:
            msg = self.commit_msg
        if msg is not None:
            msg = self._filter_comments(msg)
            return [git.GitCommit(rev="", title="", body=msg)]

        # Get commit messages from git log (--rev-range)
        return git.get_commits(end=self.rev_range)

    @staticmethod
    def _filter_comments(msg: str) -> str:
        """Filter the commit message by removing comments.

        When using `git commit --verbose`, we exclude the diff that is going to
        generated, like the following example:

        ```bash
        ...
        # ------------------------ >8 ------------------------
        # Do not modify or remove the line above.
        # Everything below it will be ignored.
        diff --git a/... b/...
        ...
        ```

        Args:
            msg: The commit message to filter.

        Returns:
            The filtered commit message without comments.
        """

        lines = []
        for line in msg.split("\n"):
            if "# ------------------------ >8 ------------------------" in line:
                break
            if not line.startswith("#"):
                lines.append(line)
        return "\n".join(lines)
