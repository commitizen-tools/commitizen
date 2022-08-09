from abc import ABCMeta, abstractmethod
from typing import Callable, Dict, List, Optional

from prompt_toolkit.styles import Style

from commitizen import defaults, git
from commitizen.config.base_config import BaseConfig
from commitizen.defaults import Questions


class BaseCommitizen(metaclass=ABCMeta):
    # Executed per message parsed by the commitizen
    changelog_message_builder_hook: Optional[
        Callable[[Dict, git.GitCommit], Dict]
    ] = None

    # Executed only at the end of the changelog generation
    changelog_hook: Optional[Callable[[str, Optional[str]], str]] = None

    def __init__(self, config: BaseConfig):
        self.config = config
        self.style = Style(self.config.settings.get("style", defaults.style))
        self.bump_pattern: Optional[str] = self.config.settings.get(
            "bump_pattern", defaults.bump_pattern
        )
        self.bump_map: Optional[Dict[str, str]] = self.config.settings.get(
            "bump_map", defaults.bump_map
        )
        self.change_type_order: Optional[List[str]] = self.config.settings.get(
            "change_type_order", defaults.change_type_order
        )
        self.change_type_map: Optional[Dict[str, str]] = self.config.settings.get(
            "change_type_map", defaults.change_type_map
        )
        self.commit_parser: Optional[str] = self.config.settings.get(
            "commit_parser", defaults.commit_parser
        )
        self.changelog_pattern: Optional[str] = self.config.settings.get(
            "changelog_pattern", defaults.changelog_pattern
        )
        self.version_parser = self.config.settings.get(
            "version_parser", defaults.version_parser
        )

    @abstractmethod
    def questions(self) -> Questions:
        """Questions regarding the commit message."""

    @abstractmethod
    def message(self, answers: dict) -> str:
        """Format your git message."""

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
