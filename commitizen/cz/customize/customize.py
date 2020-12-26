try:
    from jinja2 import Template
except ImportError:
    from string import Template  # type: ignore

from typing import Any, Dict, List, Optional

from commitizen import defaults
from commitizen.config import BaseConfig
from commitizen.cz.base import BaseCommitizen
from commitizen.exceptions import MissingCzCustomizeConfigError

__all__ = ["CustomizeCommitsCz"]


class CustomizeCommitsCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern
    bump_map = defaults.bump_map
    change_type_order = defaults.change_type_order

    def __init__(self, config: BaseConfig):
        super(CustomizeCommitsCz, self).__init__(config)

        if "customize" not in self.config.settings:
            raise MissingCzCustomizeConfigError()
        self.custom_settings = self.config.settings["customize"]

        custom_bump_pattern = self.custom_settings.get("bump_pattern")
        if custom_bump_pattern:
            self.bump_pattern = custom_bump_pattern

        custom_bump_map = self.custom_settings.get("bump_map")
        if custom_bump_map:
            self.bump_map = custom_bump_map

        custom_change_type_order = self.custom_settings.get("change_type_order")
        if custom_change_type_order:
            self.change_type_order = custom_change_type_order

    def questions(self) -> List[Dict[str, Any]]:
        return self.custom_settings.get("questions")

    def message(self, answers: dict) -> str:
        message_template = Template(self.custom_settings.get("message_template"))
        if getattr(Template, "substitute", None):
            return message_template.substitute(**answers)  # type: ignore
        else:
            return message_template.render(**answers)

    def example(self) -> Optional[str]:
        return self.custom_settings.get("example")

    def schema_pattern(self) -> Optional[str]:
        return self.custom_settings.get("schema_pattern")

    def schema(self) -> Optional[str]:
        return self.custom_settings.get("schema")

    def info(self) -> Optional[str]:
        info_path = self.custom_settings.get("info_path")
        info = self.custom_settings.get("info")
        if info_path:
            with open(info_path, "r") as f:
                content = f.read()
            return content
        elif info:
            return info
        return None
