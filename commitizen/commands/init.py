import questionary

from commitizen import factory, out
from commitizen.cz import registry
from commitizen.config import BaseConfig
from commitizen.git import get_latest_tag, get_all_tags


class Init:
    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        values_to_add = {}

        # No config file exist
        if not self.config.path:
            values_to_add["name"] = self._ask_name()
            tag = self._ask_tag()
            values_to_add["version"] = tag
            values_to_add["tag_format"] = self._ask_tag_format(tag)
        else:
            out.line(f"Config file {self.config.path} already exists")
            raise SystemExit()

        self._update_config_file(values_to_add)
        out.write("The configuration are all set.")

    def _ask_name(self) -> str:
        name = questionary.select(
            "Please choose a cz: ",
            choices=list(registry.keys()),
            default="cz_conventional_commits",
            style=self.cz.style,
        ).ask()
        return name

    def _ask_tag(self) -> str:
        latest_tag = get_latest_tag()
        is_correct_tag = questionary.confirm(
            f"Is {latest_tag} the latest tag?", style=self.cz.style, default=False
        ).ask()
        if not is_correct_tag:
            tags = get_all_tags()
            if not tags:
                out.line("No Existing Tag. Set tag to v0.0.1")
                return "v0.0.1"

            latest_tag = questionary.select(
                "Please choose the latest tag: ",
                choices=get_all_tags(),
                style=self.cz.style,
            ).ask()

            if not latest_tag:
                out.error("Tag is required!")
                raise SystemExit()
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
                "Please enter the correct version format: ", style=self.cz.style
            ).ask()

            if not tag_format:
                out.error("Tag format is required!")
                raise SystemExit()
        return tag_format

    def _update_config_file(self, values):
        if not values:
            out.write("The configuration were all set. Nothing to add.")
            raise SystemExit()

        for key, value in values.items():
            self.config.set_key(key, value)
