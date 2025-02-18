from __future__ import annotations

import sys
from typing import cast

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown
from commitizen.providers.base_provider import VersionProvider
from commitizen.providers.cargo_provider import CargoProvider
from commitizen.providers.commitizen_provider import CommitizenProvider
from commitizen.providers.composer_provider import ComposerProvider
from commitizen.providers.npm_provider import NpmProvider
from commitizen.providers.pep621_provider import Pep621Provider
from commitizen.providers.poetry_provider import PoetryProvider
from commitizen.providers.scm_provider import ScmProvider
from commitizen.providers.uv_provider import UvProvider

__all__ = [
    "get_provider",
    "CargoProvider",
    "CommitizenProvider",
    "ComposerProvider",
    "NpmProvider",
    "Pep621Provider",
    "PoetryProvider",
    "ScmProvider",
    "UvProvider",
]

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
