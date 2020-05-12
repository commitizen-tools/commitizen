from commitizen import out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig


class Version:
    """Get the version of the installed commitizen or the current project."""

    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.parameter = args[0]

    def __call__(self):
        if self.parameter.get("project"):
            version = self.config.settings["version"]
            if version:
                out.write(f"{version}")
            else:
                out.error("No project information in this project.")
        elif self.parameter.get("verbose"):
            out.write(f"Installed Commitizen Version: {__version__}")
            version = self.config.settings["version"]
            if version:
                out.write(f"Project Version: {version}")
            else:
                out.error("No project information in this project.")
        else:
            # if no argument is given, show installed commitizen version
            out.write(f"{__version__}")
