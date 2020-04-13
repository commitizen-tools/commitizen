from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from prompt_toolkit.styles import Style, merge_styles

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
        """Regex matching the schema used for message validation"""
        raise NotImplementedError("Not Implemented yet")

    def info(self) -> Optional[str]:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")
