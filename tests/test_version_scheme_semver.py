import itertools
import random

import pytest

from commitizen.bump_rule import VersionIncrement
from commitizen.version_schemes import Prerelease, SemVer, VersionProtocol

simple_flow = [
    (("0.1.0", VersionIncrement.PATCH, None, 0, None), "0.1.1"),
    (("0.1.0", VersionIncrement.PATCH, None, 0, 1), "0.1.1-dev1"),
    (("0.1.1", VersionIncrement.MINOR, None, 0, None), "0.2.0"),
    (("0.2.0", VersionIncrement.MINOR, None, 0, None), "0.3.0"),
    (("0.2.0", VersionIncrement.MINOR, None, 0, 1), "0.3.0-dev1"),
    (("0.3.0", VersionIncrement.PATCH, None, 0, None), "0.3.1"),
    (("0.3.0", VersionIncrement.PATCH, Prerelease.ALPHA, 0, None), "0.3.1-a0"),
    (("0.3.1a0", None, Prerelease.ALPHA, 0, None), "0.3.1-a1"),
    (("0.3.0", VersionIncrement.PATCH, Prerelease.ALPHA, 1, None), "0.3.1-a1"),
    (("0.3.1a0", None, Prerelease.ALPHA, 1, None), "0.3.1-a1"),
    (("0.3.1a0", None, None, 0, None), "0.3.1"),
    (("0.3.1", VersionIncrement.PATCH, None, 0, None), "0.3.2"),
    (("0.4.2", VersionIncrement.MAJOR, Prerelease.ALPHA, 0, None), "1.0.0-a0"),
    (("1.0.0a0", None, Prerelease.ALPHA, 0, None), "1.0.0-a1"),
    (("1.0.0a1", None, Prerelease.ALPHA, 0, None), "1.0.0-a2"),
    (("1.0.0a1", None, Prerelease.ALPHA, 0, 1), "1.0.0-a2-dev1"),
    (("1.0.0a2.dev0", None, Prerelease.ALPHA, 0, 1), "1.0.0-a3-dev1"),
    (("1.0.0a2.dev0", None, Prerelease.ALPHA, 0, 0), "1.0.0-a3-dev0"),
    (("1.0.0a1", None, Prerelease.BETA, 0, None), "1.0.0-b0"),
    (("1.0.0b0", None, Prerelease.BETA, 0, None), "1.0.0-b1"),
    (("1.0.0b1", None, Prerelease.RC, 0, None), "1.0.0-rc0"),
    (("1.0.0rc0", None, Prerelease.RC, 0, None), "1.0.0-rc1"),
    (("1.0.0rc0", None, Prerelease.RC, 0, 1), "1.0.0-rc1-dev1"),
    (("1.0.0rc0", VersionIncrement.PATCH, None, 0, None), "1.0.0"),
    (("1.0.0a3.dev0", None, Prerelease.BETA, 0, None), "1.0.0-b0"),
    (("1.0.0", VersionIncrement.PATCH, None, 0, None), "1.0.1"),
    (("1.0.1", VersionIncrement.PATCH, None, 0, None), "1.0.2"),
    (("1.0.2", VersionIncrement.MINOR, None, 0, None), "1.1.0"),
    (("1.1.0", VersionIncrement.MINOR, None, 0, None), "1.2.0"),
    (("1.2.0", VersionIncrement.PATCH, None, 0, None), "1.2.1"),
    (("1.2.1", VersionIncrement.MAJOR, None, 0, None), "2.0.0"),
]

local_versions = [
    (("4.5.0+0.1.0", VersionIncrement.PATCH, None, 0, None), "4.5.0+0.1.1"),
    (("4.5.0+0.1.1", VersionIncrement.MINOR, None, 0, None), "4.5.0+0.2.0"),
    (("4.5.0+0.2.0", VersionIncrement.MAJOR, None, 0, None), "4.5.0+1.0.0"),
]

# never bump backwards on pre-releases
linear_prerelease_cases = [
    (("0.1.1b1", None, Prerelease.ALPHA, 0, None), "0.1.1-b2"),
    (("0.1.1rc0", None, Prerelease.ALPHA, 0, None), "0.1.1-rc1"),
    (("0.1.1rc0", None, Prerelease.BETA, 0, None), "0.1.1-rc1"),
]

weird_cases = [
    (("1.1", VersionIncrement.PATCH, None, 0, None), "1.1.1"),
    (("1", VersionIncrement.MINOR, None, 0, None), "1.1.0"),
    (("1", VersionIncrement.MAJOR, None, 0, None), "2.0.0"),
    (("1a0", None, Prerelease.ALPHA, 0, None), "1.0.0-a1"),
    (("1a0", None, Prerelease.ALPHA, 1, None), "1.0.0-a1"),
    (("1", None, Prerelease.BETA, 0, None), "1.0.0-b0"),
    (("1", None, Prerelease.BETA, 1, None), "1.0.0-b1"),
    (("1beta", None, Prerelease.BETA, 0, None), "1.0.0-b1"),
    (("1.0.0alpha1", None, Prerelease.ALPHA, 0, None), "1.0.0-a2"),
    (("1", None, Prerelease.RC, 0, None), "1.0.0-rc0"),
    (("1.0.0rc1+e20d7b57f3eb", VersionIncrement.PATCH, None, 0, None), "1.0.0"),
]

# test driven development
tdd_cases = [
    (("0.1.1", VersionIncrement.PATCH, None, 0, None), "0.1.2"),
    (("0.1.1", VersionIncrement.MINOR, None, 0, None), "0.2.0"),
    (("2.1.1", VersionIncrement.MAJOR, None, 0, None), "3.0.0"),
    (("0.9.0", VersionIncrement.PATCH, Prerelease.ALPHA, 0, None), "0.9.1-a0"),
    (("0.9.0", VersionIncrement.MINOR, Prerelease.ALPHA, 0, None), "0.10.0-a0"),
    (("0.9.0", VersionIncrement.MAJOR, Prerelease.ALPHA, 0, None), "1.0.0-a0"),
    (("0.9.0", VersionIncrement.MAJOR, Prerelease.ALPHA, 1, None), "1.0.0-a1"),
    (("1.0.0a2", None, Prerelease.BETA, 0, None), "1.0.0-b0"),
    (("1.0.0a2", None, Prerelease.BETA, 1, None), "1.0.0-b1"),
    (("1.0.0beta1", None, Prerelease.RC, 0, None), "1.0.0-rc0"),
    (("1.0.0rc1", None, Prerelease.RC, 0, None), "1.0.0-rc2"),
    (("1.0.0-a0", None, Prerelease.RC, 0, None), "1.0.0-rc0"),
    (("1.0.0-alpha1", None, Prerelease.ALPHA, 0, None), "1.0.0-a2"),
]

exact_cases = [
    (("1.0.0", VersionIncrement.PATCH, None, 0, None), "1.0.1"),
    (("1.0.0", VersionIncrement.MINOR, None, 0, None), "1.1.0"),
    # with exact_increment=False: "1.0.0-b0"
    (("1.0.0a1", VersionIncrement.PATCH, Prerelease.BETA, 0, None), "1.0.1-b0"),
    # with exact_increment=False: "1.0.0-b1"
    (("1.0.0b0", VersionIncrement.PATCH, Prerelease.BETA, 0, None), "1.0.1-b0"),
    # with exact_increment=False: "1.0.0-rc0"
    (("1.0.0b1", VersionIncrement.PATCH, Prerelease.RC, 0, None), "1.0.1-rc0"),
    # with exact_increment=False: "1.0.0-rc1"
    (("1.0.0rc0", VersionIncrement.PATCH, Prerelease.RC, 0, None), "1.0.1-rc0"),
    # with exact_increment=False: "1.0.0-rc1-dev1"
    (("1.0.0rc0", VersionIncrement.PATCH, Prerelease.RC, 0, 1), "1.0.1-rc0-dev1"),
    # with exact_increment=False: "1.0.0-b0"
    (("1.0.0a1", VersionIncrement.MINOR, Prerelease.BETA, 0, None), "1.1.0-b0"),
    # with exact_increment=False: "1.0.0-b1"
    (("1.0.0b0", VersionIncrement.MINOR, Prerelease.BETA, 0, None), "1.1.0-b0"),
    # with exact_increment=False: "1.0.0-rc0"
    (("1.0.0b1", VersionIncrement.MINOR, Prerelease.RC, 0, None), "1.1.0-rc0"),
    # with exact_increment=False: "1.0.0-rc1"
    (("1.0.0rc0", VersionIncrement.MINOR, Prerelease.RC, 0, None), "1.1.0-rc0"),
    # with exact_increment=False: "1.0.0-rc1-dev1"
    (("1.0.0rc0", VersionIncrement.MINOR, Prerelease.RC, 0, 1), "1.1.0-rc0-dev1"),
    # with exact_increment=False: "2.0.0"
    (("2.0.0b0", VersionIncrement.MAJOR, None, 0, None), "3.0.0"),
    # with exact_increment=False: "2.0.0"
    (("2.0.0b0", VersionIncrement.MINOR, None, 0, None), "2.1.0"),
    # with exact_increment=False: "2.0.0"
    (("2.0.0b0", VersionIncrement.PATCH, None, 0, None), "2.0.1"),
    # same with exact_increment=False
    (("2.0.0b0", VersionIncrement.MAJOR, Prerelease.ALPHA, 0, None), "3.0.0-a0"),
    # with exact_increment=False: "2.0.0b1"
    (("2.0.0b0", VersionIncrement.MINOR, Prerelease.ALPHA, 0, None), "2.1.0-a0"),
    # with exact_increment=False: "2.0.0b1"
    (("2.0.0b0", VersionIncrement.PATCH, Prerelease.ALPHA, 0, None), "2.0.1-a0"),
]


@pytest.mark.parametrize(
    "test_input, expected",
    itertools.chain(tdd_cases, weird_cases, simple_flow, linear_prerelease_cases),
)
def test_bump_semver_version(test_input, expected):
    current_version = test_input[0]
    increment = test_input[1]
    prerelease = test_input[2]
    prerelease_offset = test_input[3]
    devrelease = test_input[4]
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


@pytest.mark.parametrize("test_input, expected", exact_cases)
def test_bump_semver_version_force(test_input, expected):
    current_version = test_input[0]
    increment = test_input[1]
    prerelease = test_input[2]
    prerelease_offset = test_input[3]
    devrelease = test_input[4]
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


@pytest.mark.parametrize("test_input,expected", local_versions)
def test_bump_semver_version_local(test_input, expected):
    current_version = test_input[0]
    increment = test_input[1]
    prerelease = test_input[2]
    prerelease_offset = test_input[3]
    devrelease = test_input[4]
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


def test_semver_sortable():
    test_input = [x[0][0] for x in simple_flow]
    test_input.extend([x[1] for x in simple_flow])
    # randomize
    random_input = [SemVer(x) for x in random.sample(test_input, len(test_input))]
    assert len(random_input) == len(test_input)
    sorted_result = [str(x) for x in sorted(random_input)]
    assert sorted_result == [
        "0.1.0",
        "0.1.0",
        "0.1.1-dev1",
        "0.1.1",
        "0.1.1",
        "0.2.0",
        "0.2.0",
        "0.2.0",
        "0.3.0-dev1",
        "0.3.0",
        "0.3.0",
        "0.3.0",
        "0.3.0",
        "0.3.1-a0",
        "0.3.1-a0",
        "0.3.1-a0",
        "0.3.1-a0",
        "0.3.1-a1",
        "0.3.1-a1",
        "0.3.1-a1",
        "0.3.1",
        "0.3.1",
        "0.3.1",
        "0.3.2",
        "0.4.2",
        "1.0.0-a0",
        "1.0.0-a0",
        "1.0.0-a1",
        "1.0.0-a1",
        "1.0.0-a1",
        "1.0.0-a1",
        "1.0.0-a2-dev0",
        "1.0.0-a2-dev0",
        "1.0.0-a2-dev1",
        "1.0.0-a2",
        "1.0.0-a3-dev0",
        "1.0.0-a3-dev0",
        "1.0.0-a3-dev1",
        "1.0.0-b0",
        "1.0.0-b0",
        "1.0.0-b0",
        "1.0.0-b1",
        "1.0.0-b1",
        "1.0.0-rc0",
        "1.0.0-rc0",
        "1.0.0-rc0",
        "1.0.0-rc0",
        "1.0.0-rc1-dev1",
        "1.0.0-rc1",
        "1.0.0",
        "1.0.0",
        "1.0.1",
        "1.0.1",
        "1.0.2",
        "1.0.2",
        "1.1.0",
        "1.1.0",
        "1.2.0",
        "1.2.0",
        "1.2.1",
        "1.2.1",
        "2.0.0",
    ]
