from commitizen import factory, out
from commitizen.config import BaseConfig


class Info:
    """Show in depth explanation of your rules."""

    def __init__(self, config: BaseConfig, *args: object) -> None:
        self.config: BaseConfig = config
        self.cz = factory.committer_factory(self.config)

    def __call__(self) -> None:
        out.write(self.cz.info())
