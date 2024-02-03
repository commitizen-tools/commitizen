import itertools
import random

import pytest

from commitizen.version_schemes import SemVer, VersionProtocol

simple_flow = [
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
]

local_versions = [
    (("4.5.0+0.1.0", "PATCH", None, 0, None), "4.5.0+0.1.1"),
    (("4.5.0+0.1.1", "MINOR", None, 0, None), "4.5.0+0.2.0"),
    (("4.5.0+0.2.0", "MAJOR", None, 0, None), "4.5.0+1.0.0"),
]

# never bump backwards on pre-releases
linear_prerelease_cases = [
    (("0.1.1b1", None, "alpha", 0, None), "0.1.1-b2"),
    (("0.1.1rc0", None, "alpha", 0, None), "0.1.1-rc1"),
    (("0.1.1rc0", None, "beta", 0, None), "0.1.1-rc1"),
]

weird_cases = [
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
]

# test driven development
tdd_cases = [
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
