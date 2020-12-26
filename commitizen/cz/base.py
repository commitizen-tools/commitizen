from abc import ABCMeta, abstractmethod
from typing import Callable, Dict, List, Optional, Tuple

from prompt_toolkit.styles import Style, merge_styles

from commitizen import git
from commitizen.config.base_config import BaseConfig


class BaseCommitizen(metaclass=ABCMeta):
    bump_pattern: Optional[str] = None
    bump_map: Optional[dict] = None
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
    def questions(self) -> list:
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

    def info(self) -> Optional[str]:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")

    def process_commit(self, commit: str) -> str:
        """Process commit for changelog.

        If not overwritten, it returns the first line of commit.
        """
        return commit.split("\n")[0]
