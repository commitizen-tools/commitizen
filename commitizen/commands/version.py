import platform
import sys
import warnings
from typing import TypedDict

from packaging.version import InvalidVersion

from commitizen import out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig
from commitizen.exceptions import NoVersionSpecifiedError, VersionSchemeUnknown
from commitizen.providers import get_provider
from commitizen.tags import TagRules
from commitizen.version_increment import VersionIncrement
from commitizen.version_schemes import Increment, get_version_scheme


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
    tag: bool


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
            warnings.warn(
                "`cz version --report` is deprecated and will be removed in v5. "
                "Use `cz --report` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            out.write(f"Commitizen Version: {__version__}")
            out.write(f"Python Version: {sys.version}")
            out.write(f"Operating System: {platform.system()}")
            return

        if self.arguments.get("verbose"):
            out.write(f"Installed Commitizen Version: {__version__}")

        if self.arguments.get("commitizen"):
            warnings.warn(
                "`cz version --commitizen` is deprecated and will be removed in v5. "
                "Use `cz --version` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
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
                scheme_factory = get_version_scheme(self.config.settings)
            except VersionSchemeUnknown:
                out.error("Unknown version scheme.")
                return

            try:
                version = scheme_factory(version_str)
            except InvalidVersion:
                out.error(f"Invalid version: '{version_str}'")
                return

            if next_increment_str := self.arguments.get("next"):
                if next_increment_str == "USE_GIT_COMMITS":
                    # TODO: implement USE_GIT_COMMITS by deriving the increment from
                    # git history. This requires refactoring the bump logic out of
                    # `commitizen/commands/bump.py` so it can be reused here. See #1678.
                    out.error("--next USE_GIT_COMMITS is not implemented yet.")
                    return

                next_increment = VersionIncrement.from_value(next_increment_str)
                increment: Increment | None
                if next_increment == VersionIncrement.NONE:
                    increment = None
                elif next_increment == VersionIncrement.PATCH:
                    increment = "PATCH"
                elif next_increment == VersionIncrement.MINOR:
                    increment = "MINOR"
                else:
                    increment = "MAJOR"
                version = version.bump(increment=increment)

            if self.arguments.get("major"):
                out.write(version.major)
                return
            if self.arguments.get("minor"):
                out.write(version.minor)
                return
            if self.arguments.get("patch"):
                out.write(version.micro)
                return

            display_version: str
            if self.arguments.get("tag"):
                tag_rules = TagRules.from_settings(self.config.settings)
                display_version = tag_rules.normalize_tag(version)
            else:
                display_version = str(version)

            out.write(
                f"Project Version: {display_version}"
                if self.arguments.get("verbose")
                else display_version
            )
            return

        for argument in ("major", "minor", "patch"):
            if self.arguments.get(argument):
                out.error(
                    f"{argument} can only be used with MANUAL_VERSION, --project or --verbose."
                )
                return

        if self.arguments.get("tag"):
            out.error("Tag can only be used with --project or --verbose.")
            return

        # If no arguments are provided, just show the installed commitizen version
        out.write(__version__)
