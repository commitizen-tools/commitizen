from commitizen import out
from commitizen.config import BaseConfig
from commitizen.__version__ import __version__


class Version:
    """Get the version of the installed commitizen or the current project."""

    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.parameter = args[0]
        print(args)

    def __call__(self):
        if self.parameter.get("project"):
            version = self.config.settings["version"]
            if version:
                out.write(f"Project Version: {__version__}")
            else:
                out.error(f"No project information in this project.")
        else:
            # if no argument is given, show installed commitizen version
            out.write(f"Installed Commitizen Version: {__version__}")
