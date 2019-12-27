from commitizen import factory, out
from commitizen.config import BaseConfig


class Example:
    """Show an example so people understands the rules."""

    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        out.write(self.cz.example())
