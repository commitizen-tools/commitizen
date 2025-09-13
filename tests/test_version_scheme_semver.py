from __future__ import annotations

import pytest

from commitizen.version_schemes import Increment, Prerelease, SemVer, VersionProtocol


@pytest.mark.parametrize(
    "test_input, expected",
    [
        # test driven development
        (("0.1.1", "PATCH", None, 0, None), "0.1.2"),
        (("0.1.1", "MINOR", None, 0, None), "0.2.0"),
        (("2.1.1", "MAJOR", None, 0, None), "3.0.0"),
        (("0.9.0", "PATCH", "alpha", 0, None), "0.9.1-a0"),
        (("0.9.0", "MINOR", "alpha", 0, None), "0.10.0-a0"),
        (("0.9.0", "MAJOR", "alpha", 0, None), "1.0.0-a0"),
        (("0.9.0", "MAJOR", "alpha", 1, None), "1.0.0-a1"),
        (("1.0.0a2", None, "beta", 0, None), "1.0.0-b0"),
        (("1.0.0a2", None, "beta", 1, None), "1.0.0-b1"),
        (("1.0.0beta1", None, "rc", 0, None), "1.0.0-rc0"),
        (("1.0.0rc1", None, "rc", 0, None), "1.0.0-rc2"),
        (("1.0.0-a0", None, "rc", 0, None), "1.0.0-rc0"),
        (("1.0.0-alpha1", None, "alpha", 0, None), "1.0.0-a2"),
        # weird cases
        (("1.1", "PATCH", None, 0, None), "1.1.1"),
        (("1", "MINOR", None, 0, None), "1.1.0"),
        (("1", "MAJOR", None, 0, None), "2.0.0"),
        (("1a0", None, "alpha", 0, None), "1.0.0-a1"),
        (("1a0", None, "alpha", 1, None), "1.0.0-a1"),
        (("1", None, "beta", 0, None), "1.0.0-b0"),
        (("1", None, "beta", 1, None), "1.0.0-b1"),
        (("1beta", None, "beta", 0, None), "1.0.0-b1"),
        (("1.0.0alpha1", None, "alpha", 0, None), "1.0.0-a2"),
        (("1", None, "rc", 0, None), "1.0.0-rc0"),
        (("1.0.0rc1+e20d7b57f3eb", "PATCH", None, 0, None), "1.0.0"),
        # simple flow
        (("0.1.0", "PATCH", None, 0, None), "0.1.1"),
        (("0.1.0", "PATCH", None, 0, 1), "0.1.1-dev1"),
        (("0.1.1", "MINOR", None, 0, None), "0.2.0"),
        (("0.2.0", "MINOR", None, 0, None), "0.3.0"),
        (("0.2.0", "MINOR", None, 0, 1), "0.3.0-dev1"),
        (("0.3.0", "PATCH", None, 0, None), "0.3.1"),
        (("0.3.0", "PATCH", "alpha", 0, None), "0.3.1-a0"),
        (("0.3.1a0", None, "alpha", 0, None), "0.3.1-a1"),
        (("0.3.0", "PATCH", "alpha", 1, None), "0.3.1-a1"),
        (("0.3.1a0", None, "alpha", 1, None), "0.3.1-a1"),
        (("0.3.1a0", None, None, 0, None), "0.3.1"),
        (("0.3.1", "PATCH", None, 0, None), "0.3.2"),
        (("0.4.2", "MAJOR", "alpha", 0, None), "1.0.0-a0"),
        (("1.0.0a0", None, "alpha", 0, None), "1.0.0-a1"),
        (("1.0.0a1", None, "alpha", 0, None), "1.0.0-a2"),
        (("1.0.0a1", None, "alpha", 0, 1), "1.0.0-a2-dev1"),
        (("1.0.0a2.dev0", None, "alpha", 0, 1), "1.0.0-a3-dev1"),
        (("1.0.0a2.dev0", None, "alpha", 0, 0), "1.0.0-a3-dev0"),
        (("1.0.0a1", None, "beta", 0, None), "1.0.0-b0"),
        (("1.0.0b0", None, "beta", 0, None), "1.0.0-b1"),
        (("1.0.0b1", None, "rc", 0, None), "1.0.0-rc0"),
        (("1.0.0rc0", None, "rc", 0, None), "1.0.0-rc1"),
        (("1.0.0rc0", None, "rc", 0, 1), "1.0.0-rc1-dev1"),
        (("1.0.0rc0", "PATCH", None, 0, None), "1.0.0"),
        (("1.0.0a3.dev0", None, "beta", 0, None), "1.0.0-b0"),
        (("1.0.0", "PATCH", None, 0, None), "1.0.1"),
        (("1.0.1", "PATCH", None, 0, None), "1.0.2"),
        (("1.0.2", "MINOR", None, 0, None), "1.1.0"),
        (("1.1.0", "MINOR", None, 0, None), "1.2.0"),
        (("1.2.0", "PATCH", None, 0, None), "1.2.1"),
        (("1.2.1", "MAJOR", None, 0, None), "2.0.0"),
        # linear prerelease cases (never bump backwards on pre-releases)
        (("0.1.1b1", None, "alpha", 0, None), "0.1.1-b2"),
        (("0.1.1rc0", None, "alpha", 0, None), "0.1.1-rc1"),
        (("0.1.1rc0", None, "beta", 0, None), "0.1.1-rc1"),
    ],
)
def test_bump_semver_version(
    test_input: tuple[str, Increment, Prerelease | None, int, int | None], expected: str
):
    current_version, increment, prerelease, prerelease_offset, devrelease = test_input
    assert (
        str(
            SemVer(current_version).bump(
                increment=increment,
                prerelease=prerelease,
                prerelease_offset=prerelease_offset,
                devrelease=devrelease,
            )
        )
        == expected
    )


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (("1.0.0", "PATCH", None, 0, None), "1.0.1"),
        (("1.0.0", "MINOR", None, 0, None), "1.1.0"),
        # with exact_increment=False: "1.0.0-b0"
        (("1.0.0a1", "PATCH", "beta", 0, None), "1.0.1-b0"),
        # with exact_increment=False: "1.0.0-b1"
        (("1.0.0b0", "PATCH", "beta", 0, None), "1.0.1-b0"),
        # with exact_increment=False: "1.0.0-rc0"
        (("1.0.0b1", "PATCH", "rc", 0, None), "1.0.1-rc0"),
        # with exact_increment=False: "1.0.0-rc1"
        (("1.0.0rc0", "PATCH", "rc", 0, None), "1.0.1-rc0"),
        # with exact_increment=False: "1.0.0-rc1-dev1"
        (("1.0.0rc0", "PATCH", "rc", 0, 1), "1.0.1-rc0-dev1"),
        # with exact_increment=False: "1.0.0-b0"
        (("1.0.0a1", "MINOR", "beta", 0, None), "1.1.0-b0"),
        # with exact_increment=False: "1.0.0-b1"
        (("1.0.0b0", "MINOR", "beta", 0, None), "1.1.0-b0"),
        # with exact_increment=False: "1.0.0-rc0"
        (("1.0.0b1", "MINOR", "rc", 0, None), "1.1.0-rc0"),
        # with exact_increment=False: "1.0.0-rc1"
        (("1.0.0rc0", "MINOR", "rc", 0, None), "1.1.0-rc0"),
        # with exact_increment=False: "1.0.0-rc1-dev1"
        (("1.0.0rc0", "MINOR", "rc", 0, 1), "1.1.0-rc0-dev1"),
        # with exact_increment=False: "2.0.0"
        (("2.0.0b0", "MAJOR", None, 0, None), "3.0.0"),
        # with exact_increment=False: "2.0.0"
        (("2.0.0b0", "MINOR", None, 0, None), "2.1.0"),
        # with exact_increment=False: "2.0.0"
        (("2.0.0b0", "PATCH", None, 0, None), "2.0.1"),
        # same with exact_increment=False
        (("2.0.0b0", "MAJOR", "alpha", 0, None), "3.0.0-a0"),
        # with exact_increment=False: "2.0.0b1"
        (("2.0.0b0", "MINOR", "alpha", 0, None), "2.1.0-a0"),
        # with exact_increment=False: "2.0.0b1"
        (("2.0.0b0", "PATCH", "alpha", 0, None), "2.0.1-a0"),
    ],
)
def test_bump_semver_version_force(
    test_input: tuple[str, Increment, Prerelease | None, int, int | None], expected: str
):
    current_version, increment, prerelease, prerelease_offset, devrelease = test_input
    assert (
        str(
            SemVer(current_version).bump(
                increment=increment,
                prerelease=prerelease,
                prerelease_offset=prerelease_offset,
                devrelease=devrelease,
                exact_increment=True,
            )
        )
        == expected
    )


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (("4.5.0+0.1.0", "PATCH", None, 0, None), "4.5.0+0.1.1"),
        (("4.5.0+0.1.1", "MINOR", None, 0, None), "4.5.0+0.2.0"),
        (("4.5.0+0.2.0", "MAJOR", None, 0, None), "4.5.0+1.0.0"),
    ],
)
def test_bump_semver_version_local(
    test_input: tuple[str, Increment, Prerelease | None, int, int | None], expected: str
):
    current_version, increment, prerelease, prerelease_offset, devrelease = test_input
    is_local_version = True
    assert (
        str(
            SemVer(current_version).bump(
                increment=increment,
                prerelease=prerelease,
                prerelease_offset=prerelease_offset,
                devrelease=devrelease,
                is_local_version=is_local_version,
            )
        )
        == expected
    )


def test_semver_scheme_property():
    version = SemVer("0.0.1")
    assert version.scheme is SemVer


def test_semver_implement_version_protocol():
    assert isinstance(SemVer("0.0.1"), VersionProtocol)
