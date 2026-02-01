from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from commitizen.exceptions import VersionProviderUnknown
from commitizen.providers import get_provider
from commitizen.providers.commitizen_provider import CommitizenProvider

if TYPE_CHECKING:
    from commitizen.config.base_config import BaseConfig


def test_default_version_provider_is_commitizen_config(default_config: BaseConfig):
    provider = get_provider(default_config)

    assert isinstance(provider, CommitizenProvider)


def test_raise_for_unknown_provider(default_config: BaseConfig):
    default_config.settings["version_provider"] = "unknown"
    with pytest.raises(VersionProviderUnknown):
        get_provider(default_config)
