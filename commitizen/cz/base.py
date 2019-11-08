from typing import Optional, List, Tuple
from abc import ABCMeta, abstractmethod

from prompt_toolkit.styles import Style


class BaseCommitizen(metaclass=ABCMeta):
    bump_pattern: Optional[str] = None
    bump_map: Optional[dict] = None
    DEFAULT_STYLE_CONFIG: List[Tuple[str, str]] = [
        ("qmark", "fg:#673ab7 bold"),
        ("question", "bold"),
        ("answer", "fg:#f44336 bold"),
        ("pointer", "fg:#673ab7 bold"),
        ("highlighted", "fg:#673ab7 bold"),
        ("selected", "fg:#cc5454"),
        ("separator", "fg:#cc5454"),
        ("instruction", ""),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]

    def __init__(self, config: dict):
        self.config = config
        if not self.config.get("style"):
            self.config["style"] = BaseCommitizen.DEFAULT_STYLE_CONFIG

    @abstractmethod
    def questions(self) -> list:
        """Questions regarding the commit message."""

    @abstractmethod
    def message(self, answers: dict) -> str:
        """Format your git message."""

    @property
    def style(self):
        return Style(self.config["style"])

    def example(self) -> str:
        """Example of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema(self) -> str:
        """Schema definition of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def info(self) -> str:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")
