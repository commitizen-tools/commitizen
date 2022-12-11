import platform
import sys

from commitizen import out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig
from commitizen.providers import get_provider


class Version:
    """Get the version of the installed commitizen or the current project."""

    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.parameter = args[0]
        self.operating_system = platform.system()
        self.python_version = sys.version

    def __call__(self):
        if self.parameter.get("report"):
            out.write(f"Commitizen Version: {__version__}")
            out.write(f"Python Version: {self.python_version}")
            out.write(f"Operating System: {self.operating_system}")
        elif self.parameter.get("project"):
            version = get_provider(self.config).get_version()
            if version:
                out.write(f"{version}")
            else:
                out.error("No project information in this project.")
        elif self.parameter.get("verbose"):
            out.write(f"Installed Commitizen Version: {__version__}")
            version = get_provider(self.config).get_version()
            if version:
                out.write(f"Project Version: {version}")
            else:
                out.error("No project information in this project.")
        else:
            # if no argument is given, show installed commitizen version
            out.write(f"{__version__}")
