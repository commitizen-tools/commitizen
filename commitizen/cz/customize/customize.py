from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

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
from commitizen.defaults import MAJOR, MINOR
from commitizen.exceptions import MissingCzCustomizeConfigError

__all__ = ["CustomizeCommitsCz"]


def _derive_major_version_zero(
    bump_map: Mapping[str, str],
) -> OrderedDict[str, str]:
    """Derive a ``bump_map_major_version_zero`` from a user-supplied
    ``bump_map`` by demoting any ``MAJOR`` rule to ``MINOR``.

    See #1728: when a ``cz_customize`` user supplies ``bump_map`` but not
    ``bump_map_major_version_zero``, the latter previously fell through to
    ``defaults.BUMP_MAP_MAJOR_VERSION_ZERO``, silently overriding the
    user's intent during ``major_version_zero = true`` bumps.
    """
    return OrderedDict(
        (pattern, MINOR if increment == MAJOR else increment)
        for pattern, increment in bump_map.items()
    )


class CustomizeCommitsCz(BaseCommitizen):
    bump_pattern = defaults.BUMP_PATTERN
    bump_map = defaults.BUMP_MAP
    bump_map_major_version_zero = defaults.BUMP_MAP_MAJOR_VERSION_ZERO
    change_type_order = defaults.CHANGE_TYPE_ORDER
    # A conventional-commits-style default so that ``cz_customize`` users who
    # configure ``changelog_pattern`` (and optionally ``change_type_map`` /
    # ``change_type_order``) but no explicit ``commit_parser`` still get a
    # changelog grouped by change type. The conventional prefix is optional,
    # so non-conforming subjects remain included as ungrouped messages.
    # Users with a different commit format can still override this via
    # ``customize.commit_parser`` (#466).
    commit_parser = (
        r"^((?P<change_type>[\w-]+)(?:\((?P<scope>[^()\r\n]*)\))?"
        r"(?P<breaking>!)?:\s+)?(?P<message>.+)$"
    )

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

        # When the user supplies a custom ``bump_map`` but no matching
        # ``bump_map_major_version_zero``, derive the latter so that bumps
        # under ``major_version_zero = true`` use the user's mapping rather
        # than the (totally unrelated) ``defaults.BUMP_MAP_MAJOR_VERSION_ZERO``
        # fallback. See #1728.
        if self.custom_settings.get("bump_map") and not self.custom_settings.get(
            "bump_map_major_version_zero"
        ):
            self.bump_map_major_version_zero = _derive_major_version_zero(self.bump_map)

    def questions(self) -> list[CzQuestion]:
        return self.custom_settings.get("questions", [{}])  # type: ignore[return-value]

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
