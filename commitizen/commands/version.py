import platform
import sys
from typing import TypedDict

from commitizen import out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig
from commitizen.exceptions import NoVersionSpecifiedError, VersionSchemeUnknown
from commitizen.providers import get_provider
from commitizen.version_schemes import DEFAULT_SCHEME, get_version_scheme


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
        self.parameter = arguments

    def __call__(self) -> None:
        if self.parameter.get("report"):
            out.write(f"Commitizen Version: {__version__}")
            out.write(f"Python Version: {sys.version}")
            out.write(f"Operating System: {platform.system()}")
            return

        if self.parameter.get("verbose"):
            out.write(f"Installed Commitizen Version: {__version__}")

        if self.parameter.get("commitizen") or not (
            self.parameter.get("project") or self.parameter.get("verbose")
        ):
            version = __version__
            version_scheme = DEFAULT_SCHEME(__version__)
        else:
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

        if self.parameter.get("major"):
            version = f"{version_scheme.major}"
        elif self.parameter.get("minor"):
            version = f"{version_scheme.minor}"

        out.write(
            f"Project Version: {version}" if self.parameter.get("verbose") else version
        )
