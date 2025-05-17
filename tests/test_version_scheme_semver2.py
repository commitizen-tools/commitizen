import itertools
import random

import pytest

from commitizen.bump_rule import VersionIncrement
from commitizen.version_schemes import Prerelease, SemVer2, VersionProtocol

simple_flow = [
    (("0.1.0", VersionIncrement.PATCH, None, 0, None), "0.1.1"),
    (("0.1.0", VersionIncrement.PATCH, None, 0, 1), "0.1.1-dev.1"),
    (("0.1.1", VersionIncrement.MINOR, None, 0, None), "0.2.0"),
    (("0.2.0", VersionIncrement.MINOR, None, 0, None), "0.3.0"),
    (("0.2.0", VersionIncrement.MINOR, None, 0, 1), "0.3.0-dev.1"),
    (("0.3.0", VersionIncrement.PATCH, None, 0, None), "0.3.1"),
    (("0.3.0", VersionIncrement.PATCH, Prerelease.ALPHA, 0, None), "0.3.1-alpha.0"),
    (("0.3.1-alpha.0", None, Prerelease.ALPHA, 0, None), "0.3.1-alpha.1"),
    (("0.3.0", VersionIncrement.PATCH, Prerelease.ALPHA, 1, None), "0.3.1-alpha.1"),
    (("0.3.1-alpha.0", None, Prerelease.ALPHA, 1, None), "0.3.1-alpha.1"),
    (("0.3.1-alpha.0", None, None, 0, None), "0.3.1"),
    (("0.3.1", VersionIncrement.PATCH, None, 0, None), "0.3.2"),
    (("0.4.2", VersionIncrement.MAJOR, Prerelease.ALPHA, 0, None), "1.0.0-alpha.0"),
    (("1.0.0-alpha.0", None, Prerelease.ALPHA, 0, None), "1.0.0-alpha.1"),
    (("1.0.0-alpha.1", None, Prerelease.ALPHA, 0, None), "1.0.0-alpha.2"),
    (("1.0.0-alpha.1", None, Prerelease.ALPHA, 0, 1), "1.0.0-alpha.2.dev.1"),
    (("1.0.0-alpha.2.dev.0", None, Prerelease.ALPHA, 0, 1), "1.0.0-alpha.3.dev.1"),
    (("1.0.0-alpha.2.dev.0", None, Prerelease.ALPHA, 0, 0), "1.0.0-alpha.3.dev.0"),
    (("1.0.0-alpha.1", None, Prerelease.BETA, 0, None), "1.0.0-beta.0"),
    (("1.0.0-beta.0", None, Prerelease.BETA, 0, None), "1.0.0-beta.1"),
    (("1.0.0-beta.1", None, Prerelease.RC, 0, None), "1.0.0-rc.0"),
    (("1.0.0-rc.0", None, Prerelease.RC, 0, None), "1.0.0-rc.1"),
    (("1.0.0-rc.0", None, Prerelease.RC, 0, 1), "1.0.0-rc.1.dev.1"),
    (("1.0.0-rc.0", VersionIncrement.PATCH, None, 0, None), "1.0.0"),
    (("1.0.0-alpha.3.dev.0", None, Prerelease.BETA, 0, None), "1.0.0-beta.0"),
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
    (("0.1.1-beta.1", None, Prerelease.ALPHA, 0, None), "0.1.1-beta.2"),
    (("0.1.1-rc.0", None, Prerelease.ALPHA, 0, None), "0.1.1-rc.1"),
    (("0.1.1-rc.0", None, Prerelease.BETA, 0, None), "0.1.1-rc.1"),
]

weird_cases = [
    (("1.1", VersionIncrement.PATCH, None, 0, None), "1.1.1"),
    (("1", VersionIncrement.MINOR, None, 0, None), "1.1.0"),
    (("1", VersionIncrement.MAJOR, None, 0, None), "2.0.0"),
    (("1-alpha.0", None, Prerelease.ALPHA, 0, None), "1.0.0-alpha.1"),
    (("1-alpha.0", None, Prerelease.ALPHA, 1, None), "1.0.0-alpha.1"),
    (("1", None, Prerelease.BETA, 0, None), "1.0.0-beta.0"),
    (("1", None, Prerelease.BETA, 1, None), "1.0.0-beta.1"),
    (("1-beta", None, Prerelease.BETA, 0, None), "1.0.0-beta.1"),
    (("1.0.0-alpha.1", None, Prerelease.ALPHA, 0, None), "1.0.0-alpha.2"),
    (("1", None, Prerelease.RC, 0, None), "1.0.0-rc.0"),
    (("1.0.0-rc.1+e20d7b57f3eb", VersionIncrement.PATCH, None, 0, None), "1.0.0"),
]

# test driven development
tdd_cases = [
    (("0.1.1", VersionIncrement.PATCH, None, 0, None), "0.1.2"),
    (("0.1.1", VersionIncrement.MINOR, None, 0, None), "0.2.0"),
    (("2.1.1", VersionIncrement.MAJOR, None, 0, None), "3.0.0"),
    (("0.9.0", VersionIncrement.PATCH, Prerelease.ALPHA, 0, None), "0.9.1-alpha.0"),
    (("0.9.0", VersionIncrement.MINOR, Prerelease.ALPHA, 0, None), "0.10.0-alpha.0"),
    (("0.9.0", VersionIncrement.MAJOR, Prerelease.ALPHA, 0, None), "1.0.0-alpha.0"),
    (("0.9.0", VersionIncrement.MAJOR, Prerelease.ALPHA, 1, None), "1.0.0-alpha.1"),
    (("1.0.0-alpha.2", None, Prerelease.BETA, 0, None), "1.0.0-beta.0"),
    (("1.0.0-alpha.2", None, Prerelease.BETA, 1, None), "1.0.0-beta.1"),
    (("1.0.0-beta.1", None, Prerelease.RC, 0, None), "1.0.0-rc.0"),
    (("1.0.0-rc.1", None, Prerelease.RC, 0, None), "1.0.0-rc.2"),
    (("1.0.0-alpha.0", None, Prerelease.RC, 0, None), "1.0.0-rc.0"),
    (("1.0.0-alpha.1", None, Prerelease.ALPHA, 0, None), "1.0.0-alpha.2"),
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
            SemVer2(current_version).bump(
                increment=increment,
                prerelease=prerelease,
                prerelease_offset=prerelease_offset,
                devrelease=devrelease,
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
            SemVer2(current_version).bump(
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
    version = SemVer2("0.0.1")
    assert version.scheme is SemVer2


def test_semver_implement_version_protocol():
    assert isinstance(SemVer2("0.0.1"), VersionProtocol)


def test_semver_sortable():
    test_input = [x[0][0] for x in simple_flow]
    test_input.extend([x[1] for x in simple_flow])
    # randomize
    random_input = [SemVer2(x) for x in random.sample(test_input, len(test_input))]
    assert len(random_input) == len(test_input)
    sorted_result = [str(x) for x in sorted(random_input)]
    assert sorted_result == [
        "0.1.0",
        "0.1.0",
        "0.1.1-dev.1",
        "0.1.1",
        "0.1.1",
        "0.2.0",
        "0.2.0",
        "0.2.0",
        "0.3.0-dev.1",
        "0.3.0",
        "0.3.0",
        "0.3.0",
        "0.3.0",
        "0.3.1-alpha.0",
        "0.3.1-alpha.0",
        "0.3.1-alpha.0",
        "0.3.1-alpha.0",
        "0.3.1-alpha.1",
        "0.3.1-alpha.1",
        "0.3.1-alpha.1",
        "0.3.1",
        "0.3.1",
        "0.3.1",
        "0.3.2",
        "0.4.2",
        "1.0.0-alpha.0",
        "1.0.0-alpha.0",
        "1.0.0-alpha.1",
        "1.0.0-alpha.1",
        "1.0.0-alpha.1",
        "1.0.0-alpha.1",
        "1.0.0-alpha.2.dev.0",
        "1.0.0-alpha.2.dev.0",
        "1.0.0-alpha.2.dev.1",
        "1.0.0-alpha.2",
        "1.0.0-alpha.3.dev.0",
        "1.0.0-alpha.3.dev.0",
        "1.0.0-alpha.3.dev.1",
        "1.0.0-beta.0",
        "1.0.0-beta.0",
        "1.0.0-beta.0",
        "1.0.0-beta.1",
        "1.0.0-beta.1",
        "1.0.0-rc.0",
        "1.0.0-rc.0",
        "1.0.0-rc.0",
        "1.0.0-rc.0",
        "1.0.0-rc.1.dev.1",
        "1.0.0-rc.1",
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
