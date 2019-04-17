from commitizen import out
from abc import ABCMeta, abstractmethod


class BaseCommitizen(metaclass=ABCMeta):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def questions(self):
        """Questions regarding the commit message.

        Must have 'whaaaaat' format.
        More info: https://github.com/finklabs/whaaaaat/

        :rtype: list
        """

    @abstractmethod
    def message(self, answers: dict) -> dict:
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

    def show_example(self, *args, **kwargs):
        out.write(self.example())

    def show_schema(self, *args, **kwargs):
        out.write(self.schema())

    def show_info(self, *args, **kwargs):
        out.write(self.info())
