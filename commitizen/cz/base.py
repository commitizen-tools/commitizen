import re
from abc import ABCMeta, abstractmethod
from typing import Callable, Dict, List, Optional, Tuple

from prompt_toolkit.styles import Style, merge_styles

from commitizen import git
from commitizen.config.base_config import BaseConfig
from commitizen.defaults import Questions
from commitizen.exceptions import InvalidCommitMessageError


class BaseCommitizen(metaclass=ABCMeta):
    bump_pattern: Optional[str] = None
    bump_map: Optional[Dict[str, str]] = None
    default_style_config: List[Tuple[str, str]] = [
        ("qmark", "fg:#ff9d00 bold"),
        ("question", "bold"),
        ("answer", "fg:#ff9d00 bold"),
        ("pointer", "fg:#ff9d00 bold"),
        ("highlighted", "fg:#ff9d00 bold"),
        ("selected", "fg:#cc5454"),
        ("separator", "fg:#cc5454"),
        ("instruction", ""),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]

    # The whole subject will be parsed as message by default
    # This allows supporting changelog for any rule system.
    # It can be modified per rule
    commit_parser: Optional[str] = r"(?P<message>.*)"
    changelog_pattern: Optional[str] = r".*"
    change_type_map: Optional[Dict[str, str]] = None
    change_type_order: Optional[List[str]] = None

    # Executed per message parsed by the commitizen
    changelog_message_builder_hook: Optional[
        Callable[[Dict, git.GitCommit], Dict]
    ] = None

    # Executed only at the end of the changelog generation
    changelog_hook: Optional[Callable[[str, Optional[str]], str]] = None

    def __init__(self, config: BaseConfig):
        self.config = config
        if not self.config.settings.get("style"):
            self.config.settings.update({"style": BaseCommitizen.default_style_config})

    @abstractmethod
    def questions(self) -> Questions:
        """Questions regarding the commit message."""

    @abstractmethod
    def message(self, answers: dict) -> str:
        """Format your git message."""

    @property
    def style(self):
        return merge_styles(
            [
                Style(BaseCommitizen.default_style_config),
                Style(self.config.settings["style"]),
            ]
        )

    def example(self) -> Optional[str]:
        """Example of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema(self) -> Optional[str]:
        """Schema definition of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema_pattern(self) -> Optional[str]:
        """Regex matching the schema used for message validation."""
        raise NotImplementedError("Not Implemented yet")

    def validate_commit_message(
        self, commit: git.GitCommit, pattern: str, allow_abort: bool
    ) -> bool:
        if not commit.message:
            return allow_abort
        if (
            commit.message.startswith("Merge")
            or commit.message.startswith("Revert")
            or commit.message.startswith("Pull request")
            or commit.message.startswith("fixup!")
            or commit.message.startswith("squash!")
        ):
            return True
        return bool(re.match(pattern, commit.message))

    def validate_commits(self, commits: List[git.GitCommit], allow_abort: bool):
        """
        Validate a commit. Invokes schema_pattern by default.
        Raises:
            InvalidCommitMessageError: if the provided commit does not follow the conventional pattern
        """

        pattern = self.schema_pattern()
        assert pattern is not None

        displayed_msgs_content = "\n".join(
            [
                f'commit "{commit.rev}": "{commit.message}"'
                for commit in commits
                if not self.validate_commit_message(commit, pattern, allow_abort)
            ]
        )

        if displayed_msgs_content:
            raise InvalidCommitMessageError(
                "commit validation: failed!\n"
                "please enter a commit message in the commitizen format.\n"
                f"{displayed_msgs_content}\n"
                f"pattern: {pattern}"
            )

    def info(self) -> Optional[str]:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")

    def process_commit(self, commit: str) -> str:
        """Process commit for changelog.

        If not overwritten, it returns the first line of commit.
        """
        return commit.split("\n")[0]
