from __future__ import annotations

import os
import shutil
from typing import Any, NamedTuple

import questionary
import yaml

from commitizen import cmd, factory, out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig, JsonConfig, TomlConfig, YAMLConfig
from commitizen.cz import registry
from commitizen.defaults import CONFIG_FILES, DEFAULT_SETTINGS
from commitizen.exceptions import InitFailedError, NoAnswersError
from commitizen.git import get_latest_tag_name, get_tag_names, smart_open
from commitizen.version_schemes import KNOWN_SCHEMES, Version, get_version_scheme


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


class ProjectInfo:
    """Discover information about the current folder."""

    @property
    def has_pyproject(self) -> bool:
        return os.path.isfile("pyproject.toml")

    @property
    def has_uv_lock(self) -> bool:
        return os.path.isfile("uv.lock")

    @property
    def has_setup(self) -> bool:
        return os.path.isfile("setup.py")

    @property
    def has_pre_commit_config(self) -> bool:
        return os.path.isfile(".pre-commit-config.yaml")

    @property
    def is_python_uv(self) -> bool:
        return self.has_pyproject and self.has_uv_lock

    @property
    def is_python_poetry(self) -> bool:
        if not self.has_pyproject:
            return False
        with open("pyproject.toml") as f:
            return "[tool.poetry]" in f.read()

    @property
    def is_python(self) -> bool:
        return self.has_pyproject or self.has_setup

    @property
    def is_rust_cargo(self) -> bool:
        return os.path.isfile("Cargo.toml")

    @property
    def is_npm_package(self) -> bool:
        return os.path.isfile("package.json")

    @property
    def is_php_composer(self) -> bool:
        return os.path.isfile("composer.json")

    @property
    def is_pre_commit_installed(self) -> bool:
        return bool(shutil.which("pre-commit"))


class Init:
    _PRE_COMMIT_CONFIG_PATH = ".pre-commit-config.yaml"

    def __init__(self, config: BaseConfig, *args: object) -> None:
        self.config: BaseConfig = config
        self.encoding = config.settings["encoding"]
        self.cz = factory.committer_factory(self.config)
        self.project_info = ProjectInfo()

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
        except KeyboardInterrupt:
            raise InitFailedError("Stopped by user")

        # Initialize configuration
        if "toml" in config_path:
            self.config = TomlConfig(data="", path=config_path)
        elif "json" in config_path:
            self.config = JsonConfig(data="{}", path=config_path)
        elif "yaml" in config_path:
            self.config = YAMLConfig(data="", path=config_path)

        # Collect hook data
        hook_types = questionary.checkbox(
            "What types of pre-commit hook you want to install? (Leave blank if you don't want to install)",
            choices=[
                questionary.Choice("commit-msg", checked=False),
                questionary.Choice("pre-push", checked=False),
            ],
        ).unsafe_ask()
        if hook_types:
            try:
                self._install_pre_commit_hook(hook_types)
            except InitFailedError as e:
                raise InitFailedError(f"Failed to install pre-commit hook.\n{e}")

        # Create and initialize config
        self.config.init_empty_config_content()

        self.config.set_key("name", cz_name)
        self.config.set_key("tag_format", tag_format)
        self.config.set_key("version_scheme", version_scheme)
        if version_provider == "commitizen":
            self.config.set_key("version", version.public)
        else:
            self.config.set_key("version_provider", version_provider)
        if update_changelog_on_bump:
            self.config.set_key("update_changelog_on_bump", update_changelog_on_bump)
        if major_version_zero:
            self.config.set_key("major_version_zero", major_version_zero)

        out.write("\nYou can bump the version running:\n")
        out.info("\tcz bump\n")
        out.success("Configuration complete 🚀")

    def _ask_config_path(self) -> str:
        default_path = (
            "pyproject.toml" if self.project_info.has_pyproject else ".cz.toml"
        )

        name: str = questionary.select(
            "Please choose a supported config file: ",
            choices=CONFIG_FILES,
            default=default_path,
            style=self.cz.style,
        ).unsafe_ask()
        return name

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
            default=self._default_version_provider,
        ).unsafe_ask()
        return version_provider

    @property
    def _default_version_provider(self) -> str:
        if self.project_info.is_python:
            if self.project_info.is_python_poetry:
                return "poetry"
            if self.project_info.is_python_uv:
                return "uv"
            return "pep621"

        if self.project_info.is_rust_cargo:
            return "cargo"
        if self.project_info.is_npm_package:
            return "npm"
        if self.project_info.is_php_composer:
            return "composer"

        return "commitizen"

    def _ask_version_scheme(self) -> str:
        """Ask for setting: version_scheme"""
        default_scheme = "pep440" if self.project_info.is_python else "semver"

        scheme: str = questionary.select(
            "Choose version scheme: ",
            choices=KNOWN_SCHEMES,
            style=self.cz.style,
            default=default_scheme,
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

    def _exec_install_pre_commit_hook(self, hook_types: list[str]) -> None:
        cmd_str = self._gen_pre_commit_cmd(hook_types)
        c = cmd.run(cmd_str)
        if c.return_code != 0:
            err_msg = (
                f"Error running {cmd_str}."
                "Outputs are attached below:\n"
                f"stdout: {c.out}\n"
                f"stderr: {c.err}"
            )
            raise InitFailedError(err_msg)

    def _gen_pre_commit_cmd(self, hook_types: list[str]) -> str:
        """Generate pre-commit command according to given hook types"""
        if not hook_types:
            raise ValueError("At least 1 hook type should be provided.")
        return "pre-commit install " + " ".join(
            f"--hook-type {ty}" for ty in hook_types
        )

    def _get_config_data(self) -> dict[str, Any]:
        CZ_HOOK_CONFIG = {
            "repo": "https://github.com/commitizen-tools/commitizen",
            "rev": f"v{__version__}",
            "hooks": [
                {"id": "commitizen"},
                {"id": "commitizen-branch", "stages": ["pre-push"]},
            ],
        }

        if not self.project_info.has_pre_commit_config:
            # .pre-commit-config.yaml does not exist
            return {"repos": [CZ_HOOK_CONFIG]}

        with open(self._PRE_COMMIT_CONFIG_PATH, encoding=self.encoding) as config_file:
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

    def _install_pre_commit_hook(self, hook_types: list[str] | None = None) -> None:
        config_data = self._get_config_data()
        with smart_open(
            self._PRE_COMMIT_CONFIG_PATH, "w", encoding=self.encoding
        ) as config_file:
            yaml.safe_dump(config_data, stream=config_file)

        if not self.project_info.is_pre_commit_installed:
            raise InitFailedError("pre-commit is not installed in current environment.")
        if hook_types is None:
            hook_types = ["commit-msg", "pre-push"]
        self._exec_install_pre_commit_hook(hook_types)
        out.write("commitizen pre-commit hook is now installed in your '.git'\n")
