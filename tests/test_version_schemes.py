from __future__ import annotations

import sys

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

import pytest
from pytest_mock import MockerFixture

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionSchemeUnknown
from commitizen.version_schemes import Pep440, Prerelease, SemVer, get_version_scheme


class TestPrereleaseSafeCast:
    def test_safe_cast_valid_strings(self):
        assert Prerelease.safe_cast("ALPHA") == Prerelease.ALPHA
        assert Prerelease.safe_cast("BETA") == Prerelease.BETA
        assert Prerelease.safe_cast("RC") == Prerelease.RC

    def test_safe_cast_case_insensitive(self):
        assert Prerelease.safe_cast("alpha") == Prerelease.ALPHA
        assert Prerelease.safe_cast("beta") == Prerelease.BETA
        assert Prerelease.safe_cast("rc") == Prerelease.RC
        assert Prerelease.safe_cast("Alpha") == Prerelease.ALPHA
        assert Prerelease.safe_cast("Beta") == Prerelease.BETA
        assert Prerelease.safe_cast("Rc") == Prerelease.RC

    def test_safe_cast_invalid_strings(self):
        assert Prerelease.safe_cast("invalid") is None
        assert Prerelease.safe_cast("") is None
        assert Prerelease.safe_cast("release") is None

    def test_safe_cast_non_string_values(self):
        assert Prerelease.safe_cast(None) is None
        assert Prerelease.safe_cast(1) is None
        assert Prerelease.safe_cast(True) is None
        assert Prerelease.safe_cast([]) is None
        assert Prerelease.safe_cast({}) is None
        assert Prerelease.safe_cast(Prerelease.ALPHA) is None  # enum value itself


def test_default_version_scheme_is_pep440(config: BaseConfig):
    scheme = get_version_scheme(config.settings)
    assert scheme is Pep440


def test_version_scheme_from_config(config: BaseConfig):
    config.settings["version_scheme"] = "semver"
    scheme = get_version_scheme(config.settings)
    assert scheme is SemVer


def test_version_scheme_from_name(config: BaseConfig):
    config.settings["version_scheme"] = "pep440"
    scheme = get_version_scheme(config.settings, "semver")
    assert scheme is SemVer


def test_raise_for_unknown_version_scheme(config: BaseConfig):
    with pytest.raises(VersionSchemeUnknown):
        get_version_scheme(config.settings, "unknown")


def test_version_scheme_from_deprecated_config(config: BaseConfig):
    config.settings["version_type"] = "semver"
    with pytest.warns(DeprecationWarning):
        scheme = get_version_scheme(config.settings)
    assert scheme is SemVer


def test_version_scheme_from_config_priority(config: BaseConfig):
    config.settings["version_scheme"] = "pep440"
    config.settings["version_type"] = "semver"
    with pytest.warns(DeprecationWarning):
        scheme = get_version_scheme(config.settings)
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
        get_version_scheme(config.settings, "any")
