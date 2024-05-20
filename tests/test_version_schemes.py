from __future__ import annotations

import importlib_metadata as metadata
import pytest
from pytest_mock import MockerFixture

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionSchemeUnknown
from commitizen.version_schemes import Pep440, SemVer, get_version_scheme


def test_default_version_scheme_is_pep440(config: BaseConfig):
    scheme = get_version_scheme(config)
    assert scheme is Pep440


def test_version_scheme_from_config(config: BaseConfig):
    config.settings["version_scheme"] = "semver"
    scheme = get_version_scheme(config)
    assert scheme is SemVer


def test_version_scheme_from_name(config: BaseConfig):
    config.settings["version_scheme"] = "pep440"
    scheme = get_version_scheme(config, "semver")
    assert scheme is SemVer


def test_raise_for_unknown_version_scheme(config: BaseConfig):
    with pytest.raises(VersionSchemeUnknown):
        get_version_scheme(config, "unknown")


def test_version_scheme_from_deprecated_config(config: BaseConfig):
    config.settings["version_type"] = "semver"
    with pytest.warns(DeprecationWarning):
        scheme = get_version_scheme(config)
    assert scheme is SemVer


def test_version_scheme_from_config_priority(config: BaseConfig):
    config.settings["version_scheme"] = "pep440"
    config.settings["version_type"] = "semver"
    with pytest.warns(DeprecationWarning):
        scheme = get_version_scheme(config)
    assert scheme is Pep440


def test_warn_if_version_protocol_not_implemented(
    config: BaseConfig, mocker: MockerFixture
):
    class NotVersionProtocol:
        pass

    ep = mocker.Mock()
    ep.load.return_value = NotVersionProtocol
    mocker.patch.object(metadata, "entry_points", return_value=(ep,))

    with pytest.warns(match="VersionProtocol"):
        get_version_scheme(config, "any")
