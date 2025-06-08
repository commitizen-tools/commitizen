from __future__ import annotations

from commitizen.providers.base_provider import VersionProvider


class CommitizenProvider(VersionProvider):
    """
    Default version provider: Fetch and set version in commitizen config.
    """

    def get_version(self) -> str:
        return self.config.settings["version"]  # type: ignore[return-value] # TODO: check if we can fix this by tweaking the `Settings` type

    def set_version(self, version: str) -> None:
        self.config.set_key("version", version)
