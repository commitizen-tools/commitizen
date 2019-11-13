from commitizen import out
from commitizen.__version__ import __version__


class Version:
    """Get the version of the installed commitizen."""

    def __init__(self, config: dict, *args):
        self.config: dict = config

    def __call__(self):
        out.write(__version__)
