from __future__ import annotations

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown
from commitizen.providers import get_provider
from commitizen.providers.commitizen_provider import CommitizenProvider


def test_default_version_provider_is_commitizen_config(config: BaseConfig):
    provider = get_provider(config)

    assert isinstance(provider, CommitizenProvider)


def test_raise_for_unknown_provider(config: BaseConfig):
    config.settings["version_provider"] = "unknown"
    with pytest.raises(VersionProviderUnknown):
        get_provider(config)
