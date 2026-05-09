from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from jinja2 import Template

    from commitizen.config import BaseConfig
    from commitizen.question import CzQuestion
else:
    try:
        from jinja2 import Template
    except ImportError:
        from string import Template


from commitizen import defaults
from commitizen.cz.base import BaseCommitizen
from commitizen.exceptions import MissingCzCustomizeConfigError

__all__ = ["CustomizeCommitsCz"]

_REQUIRED_ANSWER_MSG = "This answer is required."


def _required_validator(val: str) -> bool | str:
    """Return True when *val* is non-blank, otherwise an error message."""
    return True if val.strip() else _REQUIRED_ANSWER_MSG


class CustomizeCommitsCz(BaseCommitizen):
    bump_pattern = defaults.BUMP_PATTERN
    bump_map = defaults.BUMP_MAP
    bump_map_major_version_zero = defaults.BUMP_MAP_MAJOR_VERSION_ZERO
    change_type_order = defaults.CHANGE_TYPE_ORDER

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)

        if "customize" not in self.config.settings:
            raise MissingCzCustomizeConfigError()
        self.custom_settings = self.config.settings["customize"]

        for attr_name in [
            "bump_pattern",
            "bump_map",
            "bump_map_major_version_zero",
            "change_type_order",
            "commit_parser",
            "changelog_pattern",
            "change_type_map",
        ]:
            if value := self.custom_settings.get(attr_name):
                setattr(self, attr_name, value)

    def questions(self) -> list[CzQuestion]:
        raw_questions: Iterable[CzQuestion] = self.custom_settings.get(
            "questions", [{}]
        )  # type: ignore[assignment]
        result: list[CzQuestion] = []
        for raw in raw_questions:
            q: dict[str, Any] = dict(raw)
            if q.get("type") == "input" and q.pop("required", False):
                q["validate"] = _required_validator
            result.append(q)  # type: ignore[arg-type]
        return result

    def message(self, answers: Mapping[str, Any]) -> str:
        message_template = Template(self.custom_settings.get("message_template", ""))
        if getattr(Template, "substitute", None):
            return message_template.substitute(**answers)  # type: ignore[attr-defined,no-any-return] # pragma: no cover # TODO: check if we can fix this
        return message_template.render(**answers)

    def example(self) -> str:
        return self.custom_settings.get("example") or ""

    def schema_pattern(self) -> str:
        return self.custom_settings.get("schema_pattern") or ""

    def schema(self) -> str:
        return self.custom_settings.get("schema") or ""

    def info(self) -> str:
        if info_path := self.custom_settings.get("info_path"):
            return Path(info_path).read_text(encoding=self.config.settings["encoding"])
        return self.custom_settings.get("info") or ""
