from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple

import questionary
import yaml

from commitizen import cmd, factory, out, project_info
from commitizen.__version__ import __version__
from commitizen.config.factory import create_config
from commitizen.cz import registry
from commitizen.defaults import CONFIG_FILES, DEFAULT_SETTINGS
from commitizen.exceptions import InitFailedError, NoAnswersError
from commitizen.git import get_latest_tag_name, get_tag_names, smart_open
from commitizen.version_schemes import KNOWN_SCHEMES, Version, get_version_scheme

if TYPE_CHECKING:
    from commitizen.config import (
        BaseConfig,
    )


class _VersionProviderOption(NamedTuple):
    provider_name: str
    description: str

    @property
    def title(self) -> str:
        return f"{self.provider_name}: {self.description}"


_VERSION_PROVIDER_CHOICES = tuple(
    questionary.Choice(title=option.title, value=option.provider_name)
    for option in (
        _VersionProviderOption(
            provider_name="commitizen",
            description="Fetch and set version in commitizen config (default)",
        ),
        _VersionProviderOption(
            provider_name="cargo",
            description="Get and set version from Cargo.toml:project.version field",
        ),
        _VersionProviderOption(
            provider_name="composer",
            description="Get and set version from composer.json:project.version field",
        ),
        _VersionProviderOption(
            provider_name="npm",
            description="Get and set version from package.json:project.version field",
        ),
        _VersionProviderOption(
            provider_name="pep621",
            description="Get and set version from pyproject.toml:project.version field",
        ),
        _VersionProviderOption(
            provider_name="poetry",
            description="Get and set version from pyproject.toml:tool.poetry.version field",
        ),
        _VersionProviderOption(
            provider_name="uv",
            description="Get and set version from pyproject.toml and uv.lock",
        ),
        _VersionProviderOption(
            provider_name="scm",
            description="Fetch the version from git and does not need to set it back",
        ),
    )
)


class Init:
    _PRE_COMMIT_CONFIG_PATH = ".pre-commit-config.yaml"

    def __init__(self, config: BaseConfig, *args: object) -> None:
        self.config: BaseConfig = config
        self.cz = factory.committer_factory(self.config)

    def __call__(self) -> None:
        if self.config.path:
            out.line(f"Config file {self.config.path} already exists")
            return

        out.info("Welcome to commitizen!\n")
        out.line(
            "Answer the following questions to configure your project.\n"
            "For further configuration, visit:\n"
            "\n"
            "https://commitizen-tools.github.io/commitizen/config/"
            "\n"
        )

        # Collect information
        try:
            config_path = self._ask_config_path()  # select
            cz_name = self._ask_name()  # select
            version_provider = self._ask_version_provider()  # select
            tag = self._ask_tag()  # confirm & select
            version_scheme = self._ask_version_scheme()  # select
            version = get_version_scheme(self.config.settings, version_scheme)(tag)
            tag_format = self._ask_tag_format(tag)  # confirm & text
            update_changelog_on_bump = self._ask_update_changelog_on_bump()  # confirm
            major_version_zero = self._ask_major_version_zero(version)  # confirm
            hook_types: list[str] | None = questionary.checkbox(
                "What types of pre-commit hook you want to install? (Leave blank if you don't want to install)",
                choices=[
                    questionary.Choice("commit-msg", checked=False),
                    questionary.Choice("pre-push", checked=False),
                ],
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise InitFailedError("Stopped by user")

        if hook_types:
            config_data = self._get_config_data()
            with smart_open(
                self._PRE_COMMIT_CONFIG_PATH,
                "w",
                encoding=self.config.settings["encoding"],
            ) as config_file:
                yaml.safe_dump(config_data, stream=config_file)

            if not project_info.is_pre_commit_installed():
                raise InitFailedError(
                    "Failed to install pre-commit hook.\n"
                    "pre-commit is not installed in current environment."
                )

            cmd_str = "pre-commit install " + " ".join(
                f"--hook-type {ty}" for ty in hook_types
            )
            c = cmd.run(cmd_str)
            if c.return_code != 0:
                raise InitFailedError(
                    "Failed to install pre-commit hook.\n"
                    f"Error running {cmd_str}."
                    "Outputs are attached below:\n"
                    f"stdout: {c.out}\n"
                    f"stderr: {c.err}"
                )
            out.write("commitizen pre-commit hook is now installed in your '.git'\n")

        _write_config_to_file(
            path=config_path,
            cz_name=cz_name,
            version_provider=version_provider,
            version_scheme=version_scheme,
            version=version,
            tag_format=tag_format,
            update_changelog_on_bump=update_changelog_on_bump,
            major_version_zero=major_version_zero,
        )

        out.write("\nYou can bump the version running:\n")
        out.info("\tcz bump\n")
        out.success("Configuration complete 🚀")

    def _ask_config_path(self) -> Path:
        filename: str = questionary.select(
            "Please choose a supported config file: ",
            choices=CONFIG_FILES,
            default=project_info.get_default_config_filename(),
            style=self.cz.style,
        ).unsafe_ask()
        return Path(filename)

    def _ask_name(self) -> str:
        name: str = questionary.select(
            "Please choose a cz (commit rule): (default: cz_conventional_commits)",
            choices=list(registry.keys()),
            default="cz_conventional_commits",
            style=self.cz.style,
        ).unsafe_ask()
        return name

    def _ask_tag(self) -> str:
        latest_tag = get_latest_tag_name()
        if not latest_tag:
            out.error("No Existing Tag. Set tag to v0.0.1")
            return "0.0.1"

        if questionary.confirm(
            f"Is {latest_tag} the latest tag?", style=self.cz.style, default=False
        ).unsafe_ask():
            return latest_tag

        existing_tags = get_tag_names()
        if not existing_tags:
            out.error("No Existing Tag. Set tag to v0.0.1")
            return "0.0.1"

        answer: str = questionary.select(
            "Please choose the latest tag: ",
            # The latest tag is most likely with the largest number.
            # Thus, listing the existing_tags in reverse order makes more sense.
            choices=sorted(existing_tags, reverse=True),
            style=self.cz.style,
        ).unsafe_ask()

        if not answer:
            raise NoAnswersError("Tag is required!")
        return answer

    def _ask_tag_format(self, latest_tag: str) -> str:
        if latest_tag.startswith("v"):
            v_tag_format = r"v$version"
            if questionary.confirm(
                f'Is "{v_tag_format}" the correct tag format?', style=self.cz.style
            ).unsafe_ask():
                return v_tag_format

        default_format = DEFAULT_SETTINGS["tag_format"]
        tag_format: str = questionary.text(
            f'Please enter the correct version format: (default: "{default_format}")',
            style=self.cz.style,
        ).unsafe_ask()

        return tag_format or default_format

    def _ask_version_provider(self) -> str:
        """Ask for setting: version_provider"""

        version_provider: str = questionary.select(
            "Choose the source of the version:",
            choices=_VERSION_PROVIDER_CHOICES,
            style=self.cz.style,
            default=project_info.get_default_version_provider(),
        ).unsafe_ask()
        return version_provider

    def _ask_version_scheme(self) -> str:
        """Ask for setting: version_scheme"""
        scheme: str = questionary.select(
            "Choose version scheme: ",
            choices=KNOWN_SCHEMES,
            style=self.cz.style,
            default=project_info.get_default_version_scheme(),
        ).unsafe_ask()
        return scheme

    def _ask_major_version_zero(self, version: Version) -> bool:
        """Ask for setting: major_version_zero"""
        if version.major > 0:
            return False
        major_version_zero: bool = questionary.confirm(
            "Keep major version zero (0.x) during breaking changes",
            default=True,
            auto_enter=True,
        ).unsafe_ask()
        return major_version_zero

    def _ask_update_changelog_on_bump(self) -> bool:
        """Ask for setting: update_changelog_on_bump"""
        update_changelog_on_bump: bool = questionary.confirm(
            "Create changelog automatically on bump",
            default=True,
            auto_enter=True,
        ).unsafe_ask()
        return update_changelog_on_bump

    def _get_config_data(self) -> dict[str, Any]:
        CZ_HOOK_CONFIG = {
            "repo": "https://github.com/commitizen-tools/commitizen",
            "rev": f"v{__version__}",
            "hooks": [
                {"id": "commitizen"},
                {"id": "commitizen-branch", "stages": ["pre-push"]},
            ],
        }

        if not Path(".pre-commit-config.yaml").is_file():
            return {"repos": [CZ_HOOK_CONFIG]}

        with open(
            self._PRE_COMMIT_CONFIG_PATH, encoding=self.config.settings["encoding"]
        ) as config_file:
            config_data: dict[str, Any] = yaml.safe_load(config_file) or {}

        if not isinstance(repos := config_data.get("repos"), list):
            # .pre-commit-config.yaml exists but there's no "repos" key
            config_data["repos"] = [CZ_HOOK_CONFIG]
            return config_data

        # Check if commitizen pre-commit hook is already in the config
        if any("commitizen" in hook_config["repo"] for hook_config in repos):
            out.write("commitizen already in pre-commit config")
        else:
            repos.append(CZ_HOOK_CONFIG)
        return config_data


def _write_config_to_file(
    *,
    path: Path,
    cz_name: str,
    version_provider: str,
    version_scheme: str,
    version: Version,
    tag_format: str,
    update_changelog_on_bump: bool,
    major_version_zero: bool,
) -> None:
    out_config = create_config(path=path)
    out_config.init_empty_config_content()

    out_config.set_key("name", cz_name)
    out_config.set_key("tag_format", tag_format)
    out_config.set_key("version_scheme", version_scheme)
    if version_provider == "commitizen":
        out_config.set_key("version", version.public)
    else:
        out_config.set_key("version_provider", version_provider)
    if update_changelog_on_bump:
        out_config.set_key("update_changelog_on_bump", update_changelog_on_bump)
    if major_version_zero:
        out_config.set_key("major_version_zero", major_version_zero)
