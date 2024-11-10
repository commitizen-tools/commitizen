from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jinja2 import Template
else:
    try:
        from jinja2 import Template
    except ImportError:
        from string import Template


from commitizen import defaults
from commitizen.config import BaseConfig
from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions
from commitizen.exceptions import MissingCzCustomizeConfigError

__all__ = ["CustomizeCommitsCz"]


class CustomizeCommitsCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern
    bump_map = defaults.bump_map
    bump_map_major_version_zero = defaults.bump_map_major_version_zero
    change_type_order = defaults.change_type_order

    def __init__(self, config: BaseConfig):
        super().__init__(config)

        if "customize" not in self.config.settings:
            raise MissingCzCustomizeConfigError()
        self.custom_settings = self.config.settings["customize"]

        custom_bump_pattern = self.custom_settings.get("bump_pattern")
        if custom_bump_pattern:
            self.bump_pattern = custom_bump_pattern

        custom_bump_map = self.custom_settings.get("bump_map")
        if custom_bump_map:
            self.bump_map = custom_bump_map

        custom_bump_map_major_version_zero = self.custom_settings.get(
            "bump_map_major_version_zero"
        )
        if custom_bump_map_major_version_zero:
            self.bump_map_major_version_zero = custom_bump_map_major_version_zero

        custom_change_type_order = self.custom_settings.get("change_type_order")
        if custom_change_type_order:
            self.change_type_order = custom_change_type_order

        commit_parser = self.custom_settings.get("commit_parser")
        if commit_parser:
            self.commit_parser = commit_parser

        changelog_pattern = self.custom_settings.get("changelog_pattern")
        if changelog_pattern:
            self.changelog_pattern = changelog_pattern

        change_type_map = self.custom_settings.get("change_type_map")
        if change_type_map:
            self.change_type_map = change_type_map

    def questions(self) -> Questions:
        return self.custom_settings.get("questions", [{}])

    def message(self, answers: dict) -> str:
        message_template = Template(self.custom_settings.get("message_template", ""))
        if getattr(Template, "substitute", None):
            return message_template.substitute(**answers)  # type: ignore
        else:
            return message_template.render(**answers)

    def example(self) -> str:
        return self.custom_settings.get("example") or ""

    def schema_pattern(self) -> str:
        return self.custom_settings.get("schema_pattern") or ""

    def schema(self) -> str:
        return self.custom_settings.get("schema") or ""

    def info(self) -> str:
        info_path = self.custom_settings.get("info_path")
        info = self.custom_settings.get("info")
        if info_path:
            with open(info_path, encoding=self.config.settings["encoding"]) as f:
                content = f.read()
            return content
        elif info:
            return info
        return ""
