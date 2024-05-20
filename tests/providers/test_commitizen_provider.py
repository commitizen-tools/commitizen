from __future__ import annotations

from typing import TYPE_CHECKING

from commitizen.config.base_config import BaseConfig
from commitizen.providers.commitizen_provider import CommitizenProvider

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_commitizen_provider(config: BaseConfig, mocker: MockerFixture):
    config.settings["version"] = "42"
    mock = mocker.patch.object(config, "set_key")

    provider = CommitizenProvider(config)
    assert provider.get_version() == "42"

    provider.set_version("43.1")
    mock.assert_called_once_with("version", "43.1")
