from __future__ import annotations

from abc import ABC, abstractmethod
from typing import cast

import importlib_metadata as metadata

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown

PROVIDER_ENTRYPOINT = "commitizen.provider"
DEFAULT_PROVIDER = "commitizen"


class VersionProvider(ABC):
    """
    Abstract base class for version providers.

    Each version provider should inherit and implement this class.
    """

    config: BaseConfig

    def __init__(self, config: BaseConfig):
        self.config = config

    @abstractmethod
    def get_version(self) -> str:
        """
        Get the current version
        """
        ...

    @abstractmethod
    def set_version(self, version: str):
        """
        Set the new current version
        """
        ...


class CommitizenProvider(VersionProvider):
    """
    Default version provider: Fetch and set version in commitizen config.
    """

    def get_version(self) -> str:
        return self.config.settings["version"]  # type: ignore

    def set_version(self, version: str):
        self.config.set_key("version", version)


def get_provider(config: BaseConfig) -> VersionProvider:
    """
    Get the version provider as defined in the configuration

    :raises VersionProviderUnknown: if the provider named by `version_provider` is not found.
    """
    provider_name = config.settings["version_provider"] or DEFAULT_PROVIDER
    try:
        (ep,) = metadata.entry_points(name=provider_name, group=PROVIDER_ENTRYPOINT)
    except ValueError:
        raise VersionProviderUnknown(f'Version Provider "{provider_name}" unknown.')
    provider_cls = ep.load()
    return cast(VersionProvider, provider_cls(config))
