from __future__ import annotations

from typing import TYPE_CHECKING

from commitizen.providers.commitizen_provider import CommitizenProvider

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from commitizen.config.base_config import BaseConfig


def test_commitizen_provider(default_config: BaseConfig, mocker: MockerFixture):
    default_config.settings["version"] = "42"
    mock = mocker.patch.object(default_config, "set_key")

    provider = CommitizenProvider(default_config)
    assert provider.get_version() == "42"

    provider.set_version("43.1")
    mock.assert_called_once_with("version", "43.1")
