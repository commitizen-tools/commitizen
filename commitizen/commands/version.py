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
    report: bool
    project: bool
    verbose: bool
    major: bool
    minor: bool


class Version:
    """Get the version of the installed commitizen or the current project."""

    def __init__(self, config: BaseConfig, arguments: VersionArgs) -> None:
        self.config: BaseConfig = config
        self.parameter = arguments
        self.operating_system = platform.system()
        self.python_version = sys.version

    def __call__(self) -> None:
        if self.parameter.get("report"):
            out.write(f"Commitizen Version: {__version__}")
            out.write(f"Python Version: {self.python_version}")
            out.write(f"Operating System: {self.operating_system}")
            return

        if (verbose := self.parameter.get("verbose")) or self.parameter.get("project"):
            if verbose:
                out.write(f"Installed Commitizen Version: {__version__}")

            try:
                version = get_provider(self.config).get_version()
            except NoVersionSpecifiedError:
                out.error("No project information in this project.")
                return

            try:
                version_scheme = get_version_scheme(self.config.settings)
            except VersionSchemeUnknown:
                out.error("Unknown version scheme.")
                return

            _version = version_scheme(version)

            if self.parameter.get("major"):
                version = f"{_version.major}"
            elif self.parameter.get("minor"):
                version = f"{_version.minor}"

            out.write(f"Project Version: {version}" if verbose else version)
            return

        # if no argument is given, show installed commitizen version
        out.write(f"{__version__}")
