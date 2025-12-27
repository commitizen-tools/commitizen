from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, TypedDict

from commitizen import factory, git, out
from commitizen.exceptions import (
    InvalidCommandArgumentError,
    InvalidCommitMessageError,
    NoCommitsFoundError,
)

if TYPE_CHECKING:
    from commitizen.config import BaseConfig


class CheckArgs(TypedDict, total=False):
    commit_msg_file: str
    commit_msg: str
    rev_range: str
    allow_abort: bool
    message_length_limit: int | None
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
        self.max_msg_length = arguments.get(
            "message_length_limit", config.settings.get("message_length_limit", None)
        )

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
        self.cz = factory.committer_factory(self.config)

    def __call__(self) -> None:
        """Validate if commit messages follows the conventional pattern.

        Raises:
            InvalidCommitMessageError: if the commit provided does not follow the conventional pattern
            NoCommitsFoundError: if no commit is found with the given range
        """
        commits = self._get_commits()
        if not commits:
            raise NoCommitsFoundError(f"No commit found with range: '{self.rev_range}'")

        pattern = re.compile(self.cz.schema_pattern())
        invalid_commits = [
            (commit, check.errors)
            for commit in commits
            if not (
                check := self.cz.validate_commit_message(
                    commit_msg=commit.message,
                    pattern=pattern,
                    allow_abort=self.allow_abort,
                    allowed_prefixes=self.allowed_prefixes,
                    max_msg_length=self.max_msg_length,
                    commit_hash=commit.rev,
                )
            ).is_valid
        ]

        if invalid_commits:
            raise InvalidCommitMessageError(
                self.cz.format_exception_message(invalid_commits)
            )
        out.success("Commit validation: successful!")

    def _get_commit_message(self) -> str | None:
        if self.commit_msg_file is None:
            # Get commit message from command line (--message)
            return self.commit_msg

        with open(
            self.commit_msg_file, encoding=self.config.settings["encoding"]
        ) as commit_file:
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
