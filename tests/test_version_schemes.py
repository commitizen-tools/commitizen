from __future__ import annotations

from importlib import metadata
from typing import TYPE_CHECKING

import pytest

from commitizen.exceptions import VersionSchemeUnknown
from commitizen.version_schemes import Pep440, SemVer, get_version_scheme

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from commitizen.config.base_config import BaseConfig


def test_default_version_scheme_is_pep440(default_config: BaseConfig):
    scheme = get_version_scheme(default_config.settings)
    assert scheme is Pep440


def test_version_scheme_from_config(default_config: BaseConfig):
    default_config.settings["version_scheme"] = "semver"
    scheme = get_version_scheme(default_config.settings)
    assert scheme is SemVer


def test_version_scheme_from_name(default_config: BaseConfig):
    default_config.settings["version_scheme"] = "pep440"
    scheme = get_version_scheme(default_config.settings, "semver")
    assert scheme is SemVer


def test_raise_for_unknown_version_scheme(default_config: BaseConfig):
    with pytest.raises(VersionSchemeUnknown):
        get_version_scheme(default_config.settings, "unknown")


def test_version_scheme_from_deprecated_config(default_config: BaseConfig):
    default_config.settings["version_type"] = "semver"
    with pytest.warns(DeprecationWarning, match="Please use `version_scheme` instead"):
        scheme = get_version_scheme(default_config.settings)
    assert scheme is SemVer


def test_version_scheme_from_config_priority(default_config: BaseConfig):
    default_config.settings["version_scheme"] = "pep440"
    default_config.settings["version_type"] = "semver"
    with pytest.warns(DeprecationWarning, match="Please use `version_scheme` instead"):
        scheme = get_version_scheme(default_config.settings)
    assert scheme is Pep440


def test_warn_if_version_protocol_not_implemented(
    default_config: BaseConfig, mocker: MockerFixture
):
    class NotVersionProtocol:
        pass

    ep = mocker.Mock()
    ep.load.return_value = NotVersionProtocol
    mocker.patch.object(metadata, "entry_points", return_value=(ep,))

    with pytest.warns() as warnings:
        get_version_scheme(default_config.settings, "any")
    assert "Version scheme any does not implement the VersionProtocol" in str(
        warnings[0].message
    )
