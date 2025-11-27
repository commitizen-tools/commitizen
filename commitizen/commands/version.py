import platform
import sys
from typing import TypedDict

from commitizen import out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig
from commitizen.exceptions import NoVersionSpecifiedError, VersionSchemeUnknown
from commitizen.providers import get_provider
from commitizen.version_schemes import get_version_scheme


class VersionArgs(TypedDict, total=False):
    commitizen: bool
    report: bool
    project: bool
    verbose: bool
    major: bool
    minor: bool


class Version:
    """Get the version of the installed commitizen or the current project.
    Precedence:
    1. report
    2. commitizen
    3. verbose, project
    """

    def __init__(self, config: BaseConfig, arguments: VersionArgs) -> None:
        self.config: BaseConfig = config
        self.arguments = arguments

    def __call__(self) -> None:
        if self.arguments.get("report"):
            out.write(f"Commitizen Version: {__version__}")
            out.write(f"Python Version: {sys.version}")
            out.write(f"Operating System: {platform.system()}")
            return

        if self.arguments.get("verbose"):
            out.write(f"Installed Commitizen Version: {__version__}")

        if not self.arguments.get("commitizen") and (
            self.arguments.get("project") or self.arguments.get("verbose")
        ):
            try:
                version = get_provider(self.config).get_version()
            except NoVersionSpecifiedError:
                out.error("No project information in this project.")
                return
            try:
                version_scheme = get_version_scheme(self.config.settings)(version)
            except VersionSchemeUnknown:
                out.error("Unknown version scheme.")
                return

            if self.arguments.get("major"):
                version = f"{version_scheme.major}"
            elif self.arguments.get("minor"):
                version = f"{version_scheme.minor}"

            out.write(
                f"Project Version: {version}"
                if self.arguments.get("verbose")
                else version
            )
            return

        if self.arguments.get("major") or self.arguments.get("minor"):
            out.error(
                "Major or minor version can only be used with --project or --verbose."
            )
            return

        # If no arguments are provided, just show the installed commitizen version
        out.write(__version__)
