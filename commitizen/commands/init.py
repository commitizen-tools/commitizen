import questionary
import tomlkit
from tomlkit.toml_file import TOMLFile

from commitizen import factory, out
from commitizen.config import _conf
from commitizen.git import get_latest_tag, get_all_tags


class Init:
    def __init__(self, config: dict, *args):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        values_to_add = {}

        if "version" not in self.config:
            tag = self._ask_tag()
            values_to_add["version"] = tag
        else:
            tag = self.config["version"]

        if not "tag_format" not in self.config:
            tag_format = self._ask_tag_format(tag)
            values_to_add["tag_format"] = tag_format

        self._update_config_file(values_to_add)
        out.write("The configuration are all set.")

    def _ask_tag(self) -> str:
        latest_tag = get_latest_tag()
        is_correct_tag = questionary.confirm(
            f"Is {latest_tag} the latest tag?", style=self.cz.style, default=False
        ).ask()
        if not is_correct_tag:
            tags = get_all_tags()
            # TODO: handle the case that no tag exists in the project
            if not tags:
                out.error("No Existing Tag")
                raise SystemExit()

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

        with open(_conf._path, "r") as f:
            toml_config = tomlkit.parse(f.read())

        for key, value in values.items():
            toml_config["tool"]["commitizen"][key] = value

        config_file = TOMLFile(_conf._path)
        config_file.write(toml_config)
