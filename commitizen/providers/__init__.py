from __future__ import annotations

from typing import cast

import importlib_metadata as metadata

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown

from .base_provider import VersionProvider

PROVIDER_ENTRYPOINT = "commitizen.provider"
DEFAULT_PROVIDER = "commitizen"


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
