from __future__ import annotations

import re
import sys
from typing import TypedDict

from commitizen import factory, git, out
from commitizen.config import BaseConfig
from commitizen.exceptions import (
    InvalidCommandArgumentError,
    InvalidCommitMessageError,
    NoCommitsFoundError,
)


class CheckArgs(TypedDict, total=False):
    commit_msg_file: str
    commit_msg: str
    rev_range: str
    allow_abort: bool
    message_length_limit: int
    allowed_prefixes: list[str]
    message: str
    use_default_range: bool


class Check:
    """Check if the current commit msg matches the commitizen format."""

    def __init__(self, config: BaseConfig, arguments: CheckArgs, *args: object) -> None:
        """Initial check command.

        Args:
            config: The config object required for the command to perform its action
            arguments: All the flags provided by the user
            cwd: Current work directory
        """
        self.commit_msg_file = arguments.get("commit_msg_file")
        self.commit_msg = arguments.get("message")
        self.rev_range = arguments.get("rev_range")
        self.allow_abort = bool(
            arguments.get("allow_abort", config.settings["allow_abort"])
        )
        self.use_default_range = bool(arguments.get("use_default_range"))
        self.max_msg_length = arguments.get("message_length_limit", 0)

        # we need to distinguish between None and [], which is a valid value
        allowed_prefixes = arguments.get("allowed_prefixes")
        self.allowed_prefixes: list[str] = (
            allowed_prefixes
            if allowed_prefixes is not None
            else config.settings["allowed_prefixes"]
        )

        num_exclusive_args_provided = sum(
            arg is not None
            for arg in (
                self.commit_msg_file,
                self.commit_msg,
                self.rev_range,
            )
        )

        if num_exclusive_args_provided > 1:
            raise InvalidCommandArgumentError(
                "Only one of --rev-range, --message, and --commit-msg-file is permitted by check command! "
                "See 'cz check -h' for more information"
            )

        if num_exclusive_args_provided == 0 and not sys.stdin.isatty():
            self.commit_msg = sys.stdin.read()

        self.config: BaseConfig = config
        self.encoding = config.settings["encoding"]
        self.cz = factory.committer_factory(self.config)

    def __call__(self) -> None:
        """Validate if commit messages follows the conventional pattern.

        Raises:
            InvalidCommitMessageError: if the commit provided not follows the conventional pattern
        """
        commits = self._get_commits()
        if not commits:
            raise NoCommitsFoundError(f"No commit found with range: '{self.rev_range}'")

        pattern = re.compile(self.cz.schema_pattern())
        invalid_msgs_content = "\n".join(
            f'commit "{commit.rev}": "{commit.message}"'
            for commit in commits
            if not self._validate_commit_message(commit.message, pattern)
        )
        if invalid_msgs_content:
            # TODO: capitalize the first letter of the error message for consistency in v5
            raise InvalidCommitMessageError(
                "commit validation: failed!\n"
                "please enter a commit message in the commitizen format.\n"
                f"{invalid_msgs_content}\n"
                f"pattern: {pattern.pattern}"
            )
        out.success("Commit validation: successful!")

    def _get_commit_message(self) -> str | None:
        if self.commit_msg_file is None:
            # Get commit message from command line (--message)
            return self.commit_msg

        with open(self.commit_msg_file, encoding=self.encoding) as commit_file:
            # Get commit message from file (--commit-msg-file)
            return commit_file.read()

    def _get_commits(self) -> list[git.GitCommit]:
        if (msg := self._get_commit_message()) is not None:
            return [git.GitCommit(rev="", title="", body=self._filter_comments(msg))]

        # Get commit messages from git log (--rev-range)
        return git.get_commits(
            git.get_default_branch() if self.use_default_range else None,
            self.rev_range,
        )

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

        lines: list[str] = []
        for line in msg.split("\n"):
            if "# ------------------------ >8 ------------------------" in line:
                break
            if not line.startswith("#"):
                lines.append(line)
        return "\n".join(lines)

    def _validate_commit_message(
        self, commit_msg: str, pattern: re.Pattern[str]
    ) -> bool:
        if not commit_msg:
            return self.allow_abort

        if any(map(commit_msg.startswith, self.allowed_prefixes)):
            return True

        if self.max_msg_length:
            msg_len = len(commit_msg.partition("\n")[0].strip())
            if msg_len > self.max_msg_length:
                return False

        return bool(pattern.match(commit_msg))
