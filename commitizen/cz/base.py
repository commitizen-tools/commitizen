from typing import Optional
from abc import ABCMeta, abstractmethod


class BaseCommitizen(metaclass=ABCMeta):
    bump_pattern: Optional[str] = None
    bump_map: Optional[dict] = None

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def questions(self) -> list:
        """Questions regarding the commit message."""

    @abstractmethod
    def message(self, answers: dict) -> str:
        """Format your git message."""

    def example(self) -> str:
        """Example of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema(self) -> str:
        """Schema definition of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def info(self) -> str:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")
