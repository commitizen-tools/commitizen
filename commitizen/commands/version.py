import platform
import sys
from typing import TypedDict

from packaging.version import InvalidVersion

from commitizen import out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig
from commitizen.exceptions import NoVersionSpecifiedError, VersionSchemeUnknown
from commitizen.providers import get_provider
from commitizen.version_increment import VersionIncrement
from commitizen.version_schemes import get_version_scheme


class VersionArgs(TypedDict, total=False):
    manual_version: str | None
    next: str | None

    # Exclusive groups 1
    commitizen: bool
    report: bool
    project: bool
    verbose: bool

    # Exclusive groups 2
    major: bool
    minor: bool
    patch: bool


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

        if self.arguments.get("commitizen"):
            out.write(__version__)
            return

        if (
            self.arguments.get("project")
            or self.arguments.get("verbose")
            or self.arguments.get("next")
            or self.arguments.get("manual_version")
        ):
            version_str = self.arguments.get("manual_version")
            if version_str is None:
                try:
                    version_str = get_provider(self.config).get_version()
                except NoVersionSpecifiedError:
                    out.error("No project information in this project.")
                    return
            try:
                version_scheme = get_version_scheme(self.config.settings)
            except VersionSchemeUnknown:
                out.error("Unknown version scheme.")
                return

            try:
                version = version_scheme(version_str)
            except InvalidVersion:
                out.error(f"Invalid version: '{version_str}'")
                return

            if next_increment_str := self.arguments.get("next"):
                if next_increment_str == "USE_GIT_COMMITS":
                    # TODO: implement this
                    raise NotImplementedError("USE_GIT_COMMITS is not implemented")

                next_increment = VersionIncrement.safe_cast(next_increment_str)
                # TODO: modify the interface of bump to accept VersionIncrement
                version = version.bump(increment=str(next_increment))  # type: ignore[arg-type]

            if self.arguments.get("major"):
                out.write(version.major)
                return
            if self.arguments.get("minor"):
                out.write(version.minor)
                return
            if self.arguments.get("patch"):
                out.write(version.micro)
                return

            out.write(
                f"Project Version: {version}"
                if self.arguments.get("verbose")
                else version
            )
            return

        for argument in ("major", "minor", "patch"):
            if self.arguments.get(argument):
                out.error(
                    f"{argument} can only be used with MANUAL_VERSION, --project or --verbose."
                )
                return

        # If no arguments are provided, just show the installed commitizen version
        out.write(__version__)
