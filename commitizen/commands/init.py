import questionary
from packaging.version import Version

from commitizen import factory, out
from commitizen.config import BaseConfig, IniConfig, TomlConfig
from commitizen.cz import registry
from commitizen.defaults import long_term_support_config_files
from commitizen.exceptions import NoAnswersError
from commitizen.git import get_latest_tag_name, get_tag_names


class Init:
    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        values_to_add = {}

        # No config for commitizen exist
        if not self.config.path:
            config_path = self._ask_config_path()

            if "toml" in config_path:
                self.config = TomlConfig(data="", path=config_path)
            else:
                self.config = IniConfig(data="", path=config_path)

            self.config.init_empty_config_content()

            values_to_add["name"] = self._ask_name()
            tag = self._ask_tag()
            values_to_add["version"] = Version(tag).public
            values_to_add["tag_format"] = self._ask_tag_format(tag)
            self._update_config_file(values_to_add)
            out.write("You can bump the version and create changelog running:\n")
            out.info("cz bump --changelog")
            out.success("The configuration are all set.")
        else:
            # TODO: handle the case that config file exist but no value
            out.line(f"Config file {self.config.path} already exists")

    def _ask_config_path(self) -> str:
        name = questionary.select(
            "Please choose a supported config file: (default: pyproject.toml)",
            choices=long_term_support_config_files,
            default="pyproject.toml",
            style=self.cz.style,
        ).ask()
        return name

    def _ask_name(self) -> str:
        name = questionary.select(
            "Please choose a cz (commit rule): (default: cz_conventional_commits)",
            choices=list(registry.keys()),
            default="cz_conventional_commits",
            style=self.cz.style,
        ).ask()
        return name

    def _ask_tag(self) -> str:
        latest_tag = get_latest_tag_name()
        if not latest_tag:
            out.error("No Existing Tag. Set tag to v0.0.1")
            return "0.0.1"

        is_correct_tag = questionary.confirm(
            f"Is {latest_tag} the latest tag?", style=self.cz.style, default=False
        ).ask()
        if not is_correct_tag:
            tags = get_tag_names()
            if not tags:
                out.error("No Existing Tag. Set tag to v0.0.1")
                return "0.0.1"

            latest_tag = questionary.select(
                "Please choose the latest tag: ",
                choices=get_tag_names(),
                style=self.cz.style,
            ).ask()

            if not latest_tag:
                raise NoAnswersError("Tag is required!")
        return latest_tag

    def _ask_tag_format(self, latest_tag) -> str:
        is_correct_format = False
        if latest_tag.startswith("v"):
            tag_format = r"v$version"
            is_correct_format = questionary.confirm(
                f'Is "{tag_format}" the correct tag format?', style=self.cz.style
            ).ask()

        if not is_correct_format:
            tag_format = questionary.text(
                'Please enter the correct version format: (default: "$version")',
                style=self.cz.style,
            ).ask()

            if not tag_format:
                tag_format = "$version"
        return tag_format

    def _update_config_file(self, values):
        for key, value in values.items():
            self.config.set_key(key, value)
