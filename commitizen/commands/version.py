from commitizen import out
from commitizen.config import BaseConfig
from commitizen.__version__ import __version__


class Version:
    """Get the version of the installed commitizen."""

    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config

    def __call__(self):
        out.write(__version__)
