from __future__ import annotations

from commitizen.exceptions import NoVersionSpecifiedError
from commitizen.providers.base_provider import VersionProvider


class CommitizenProvider(VersionProvider):
    """
    Default version provider: Fetch and set version in commitizen config.
    """

    def get_version(self) -> str:
        if ret := self.config.settings["version"]:
            return ret
        raise NoVersionSpecifiedError()

    def set_version(self, version: str) -> None:
        self.config.set_key("version", version)
