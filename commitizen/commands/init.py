from __future__ import annotations

import os
import shutil
from typing import Any

import questionary
import yaml

from commitizen import cmd, factory, out
from commitizen.__version__ import __version__
from commitizen.config import BaseConfig, JsonConfig, TomlConfig, YAMLConfig
from commitizen.cz import registry
from commitizen.defaults import DEFAULT_SETTINGS, config_files
from commitizen.exceptions import InitFailedError, NoAnswersError
from commitizen.git import get_latest_tag_name, get_tag_names, smart_open
from commitizen.version_schemes import KNOWN_SCHEMES, Version, get_version_scheme


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
    def latest_tag(self) -> str | None:
        return get_latest_tag_name()

    def tags(self) -> list | None:
        """Not a property, only use if necessary"""
        if self.latest_tag is None:
            return None
        return get_tag_names()

    @property
    def is_pre_commit_installed(self) -> bool:
        return bool(shutil.which("pre-commit"))


class Init:
    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.encoding = config.settings["encoding"]
        self.cz = factory.commiter_factory(self.config)
        self.project_info = ProjectInfo()

    def __call__(self):
        if self.config.path:
            out.line(f"Config file {self.config.path} already exists")
            return

        out.info("Welcome to commitizen!\n")
        out.line(
            "Answer the questions to configure your project.\n"
            "For further configuration visit:\n"
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
        values_to_add = {}
        values_to_add["name"] = cz_name
        values_to_add["tag_format"] = tag_format
        values_to_add["version_scheme"] = version_scheme

        if version_provider == "commitizen":
            values_to_add["version"] = version.public
        else:
            values_to_add["version_provider"] = version_provider

        if update_changelog_on_bump:
            values_to_add["update_changelog_on_bump"] = update_changelog_on_bump

        if major_version_zero:
            values_to_add["major_version_zero"] = major_version_zero

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
        self._update_config_file(values_to_add)

        out.write("\nYou can bump the version running:\n")
        out.info("\tcz bump\n")
        out.success("Configuration complete 🚀")

    def _ask_config_path(self) -> str:
        default_path = ".cz.toml"
        if self.project_info.has_pyproject:
            default_path = "pyproject.toml"

        name: str = questionary.select(
            "Please choose a supported config file: ",
            choices=config_files,
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
        latest_tag = self.project_info.latest_tag
        if not latest_tag:
            out.error("No Existing Tag. Set tag to v0.0.1")
            return "0.0.1"

        is_correct_tag = questionary.confirm(
            f"Is {latest_tag} the latest tag?", style=self.cz.style, default=False
        ).unsafe_ask()
        if not is_correct_tag:
            tags = self.project_info.tags()
            if not tags:
                out.error("No Existing Tag. Set tag to v0.0.1")
                return "0.0.1"

            # the latest tag is most likely with the largest number. Thus list the tags in reverse order makes more sense
            sorted_tags = sorted(tags, reverse=True)
            latest_tag = questionary.select(
                "Please choose the latest tag: ",
                choices=sorted_tags,
                style=self.cz.style,
            ).unsafe_ask()

            if not latest_tag:
                raise NoAnswersError("Tag is required!")
        return latest_tag

    def _ask_tag_format(self, latest_tag) -> str:
        is_correct_format = False
        if latest_tag.startswith("v"):
            tag_format = r"v$version"
            is_correct_format = questionary.confirm(
                f'Is "{tag_format}" the correct tag format?', style=self.cz.style
            ).unsafe_ask()

        default_format = DEFAULT_SETTINGS["tag_format"]
        if not is_correct_format:
            tag_format = questionary.text(
                f'Please enter the correct version format: (default: "{default_format}")',
                style=self.cz.style,
            ).unsafe_ask()

            if not tag_format:
                tag_format = default_format
        return tag_format

    def _ask_version_provider(self) -> str:
        """Ask for setting: version_provider"""

        OPTS = {
            "commitizen": "commitizen: Fetch and set version in commitizen config (default)",
            "cargo": "cargo: Get and set version from Cargo.toml:project.version field",
            "composer": "composer: Get and set version from composer.json:project.version field",
            "npm": "npm: Get and set version from package.json:project.version field",
            "pep621": "pep621: Get and set version from pyproject.toml:project.version field",
            "poetry": "poetry: Get and set version from pyproject.toml:tool.poetry.version field",
            "uv": "uv: Get and Get and set version from pyproject.toml and uv.lock",
            "scm": "scm: Fetch the version from git and does not need to set it back",
        }

        default_val = "commitizen"
        if self.project_info.is_python:
            if self.project_info.is_python_poetry:
                default_val = "poetry"
            elif self.project_info.is_python_uv:
                default_val = "uv"
            else:
                default_val = "pep621"
        elif self.project_info.is_rust_cargo:
            default_val = "cargo"
        elif self.project_info.is_npm_package:
            default_val = "npm"
        elif self.project_info.is_php_composer:
            default_val = "composer"

        choices = [
            questionary.Choice(title=title, value=value)
            for value, title in OPTS.items()
        ]
        default = next(filter(lambda x: x.value == default_val, choices))
        version_provider: str = questionary.select(
            "Choose the source of the version:",
            choices=choices,
            style=self.cz.style,
            default=default,
        ).unsafe_ask()
        return version_provider

    def _ask_version_scheme(self) -> str:
        """Ask for setting: version_scheme"""
        default = "semver"
        if self.project_info.is_python:
            default = "pep440"

        scheme: str = questionary.select(
            "Choose version scheme: ",
            choices=list(KNOWN_SCHEMES),
            style=self.cz.style,
            default=default,
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
        "Ask for setting: update_changelog_on_bump"
        update_changelog_on_bump: bool = questionary.confirm(
            "Create changelog automatically on bump",
            default=True,
            auto_enter=True,
        ).unsafe_ask()
        return update_changelog_on_bump

    def _exec_install_pre_commit_hook(self, hook_types: list[str]):
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
        cmd_str = "pre-commit install " + " ".join(
            f"--hook-type {ty}" for ty in hook_types
        )
        return cmd_str

    def _install_pre_commit_hook(self, hook_types: list[str] | None = None):
        pre_commit_config_filename = ".pre-commit-config.yaml"
        cz_hook_config = {
            "repo": "https://github.com/commitizen-tools/commitizen",
            "rev": f"v{__version__}",
            "hooks": [
                {"id": "commitizen"},
                {"id": "commitizen-branch", "stages": ["push"]},
            ],
        }

        config_data = {}
        if not self.project_info.has_pre_commit_config:
            # .pre-commit-config.yaml does not exist
            config_data["repos"] = [cz_hook_config]
        else:
            with open(
                pre_commit_config_filename, encoding=self.encoding
            ) as config_file:
                yaml_data = yaml.safe_load(config_file)
                if yaml_data:
                    config_data = yaml_data

            if "repos" in config_data:
                for pre_commit_hook in config_data["repos"]:
                    if "commitizen" in pre_commit_hook["repo"]:
                        out.write("commitizen already in pre-commit config")
                        break
                else:
                    config_data["repos"].append(cz_hook_config)
            else:
                # .pre-commit-config.yaml exists but there's no "repos" key
                config_data["repos"] = [cz_hook_config]

        with smart_open(
            pre_commit_config_filename, "w", encoding=self.encoding
        ) as config_file:
            yaml.safe_dump(config_data, stream=config_file)

        if not self.project_info.is_pre_commit_installed:
            raise InitFailedError("pre-commit is not installed in current environment.")
        if hook_types is None:
            hook_types = ["commit-msg", "pre-push"]
        self._exec_install_pre_commit_hook(hook_types)
        out.write("commitizen pre-commit hook is now installed in your '.git'\n")

    def _update_config_file(self, values: dict[str, Any]):
        for key, value in values.items():
            self.config.set_key(key, value)
