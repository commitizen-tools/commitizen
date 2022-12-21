import itertools

import pytest
from packaging.version import Version

from commitizen.bump import generate_version

simple_flow = [
    (("0.1.0", "PATCH", None, 0, None), "0.1.1"),
    (("0.1.0", "PATCH", None, 0, 1), "0.1.1.dev1"),
    (("0.1.1", "MINOR", None, 0, None), "0.2.0"),
    (("0.2.0", "MINOR", None, 0, None), "0.3.0"),
    (("0.2.0", "MINOR", None, 0, 1), "0.3.0.dev1"),
    (("0.3.0", "PATCH", None, 0, None), "0.3.1"),
    (("0.3.0", "PATCH", "alpha", 0, None), "0.3.1a0"),
    (("0.3.1a0", None, "alpha", 0, None), "0.3.1a1"),
    (("0.3.0", "PATCH", "alpha", 1, None), "0.3.1a1"),
    (("0.3.1a0", None, "alpha", 1, None), "0.3.1a1"),
    (("0.3.1a0", None, None, 0, None), "0.3.1"),
    (("0.3.1", "PATCH", None, 0, None), "0.3.2"),
    (("0.4.2", "MAJOR", "alpha", 0, None), "1.0.0a0"),
    (("1.0.0a0", None, "alpha", 0, None), "1.0.0a1"),
    (("1.0.0a1", None, "alpha", 0, None), "1.0.0a2"),
    (("1.0.0a1", None, "alpha", 0, 1), "1.0.0a2.dev1"),
    (("1.0.0a2.dev0", None, "alpha", 0, 1), "1.0.0a3.dev1"),
    (("1.0.0a2.dev0", None, "alpha", 0, 0), "1.0.0a3.dev0"),
    (("1.0.0a1", None, "beta", 0, None), "1.0.0b0"),
    (("1.0.0b0", None, "beta", 0, None), "1.0.0b1"),
    (("1.0.0b1", None, "rc", 0, None), "1.0.0rc0"),
    (("1.0.0rc0", None, "rc", 0, None), "1.0.0rc1"),
    (("1.0.0rc0", None, "rc", 0, 1), "1.0.0rc1.dev1"),
    (("1.0.0rc0", "PATCH", None, 0, None), "1.0.0"),
    (("1.0.0a3.dev0", None, "beta", 0, None), "1.0.0b0"),
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

# this cases should be handled gracefully
unexpected_cases = [
    (("0.1.1rc0", None, "alpha", 0, None), "0.1.1a0"),
    (("0.1.1b1", None, "alpha", 0, None), "0.1.1a0"),
]

weird_cases = [
    (("1.1", "PATCH", None, 0, None), "1.1.1"),
    (("1", "MINOR", None, 0, None), "1.1.0"),
    (("1", "MAJOR", None, 0, None), "2.0.0"),
    (("1a0", None, "alpha", 0, None), "1.0.0a1"),
    (("1a0", None, "alpha", 1, None), "1.0.0a1"),
    (("1", None, "beta", 0, None), "1.0.0b0"),
    (("1", None, "beta", 1, None), "1.0.0b1"),
    (("1beta", None, "beta", 0, None), "1.0.0b1"),
    (("1.0.0alpha1", None, "alpha", 0, None), "1.0.0a2"),
    (("1", None, "rc", 0, None), "1.0.0rc0"),
    (("1.0.0rc1+e20d7b57f3eb", "PATCH", None, 0, None), "1.0.0"),
]

# test driven development
tdd_cases = [
    (("0.1.1", "PATCH", None, 0, None), "0.1.2"),
    (("0.1.1", "MINOR", None, 0, None), "0.2.0"),
    (("2.1.1", "MAJOR", None, 0, None), "3.0.0"),
    (("0.9.0", "PATCH", "alpha", 0, None), "0.9.1a0"),
    (("0.9.0", "MINOR", "alpha", 0, None), "0.10.0a0"),
    (("0.9.0", "MAJOR", "alpha", 0, None), "1.0.0a0"),
    (("0.9.0", "MAJOR", "alpha", 1, None), "1.0.0a1"),
    (("1.0.0a2", None, "beta", 0, None), "1.0.0b0"),
    (("1.0.0a2", None, "beta", 1, None), "1.0.0b1"),
    (("1.0.0beta1", None, "rc", 0, None), "1.0.0rc0"),
    (("1.0.0rc1", None, "rc", 0, None), "1.0.0rc2"),
]


@pytest.mark.parametrize(
    "test_input,expected",
    itertools.chain(tdd_cases, weird_cases, simple_flow, unexpected_cases),
)
def test_generate_version(test_input, expected):
    current_version = test_input[0]
    increment = test_input[1]
    prerelease = test_input[2]
    prerelease_offset = test_input[3]
    devrelease = test_input[4]
    assert (
        generate_version(
            current_version,
            increment=increment,
            prerelease=prerelease,
            prerelease_offset=prerelease_offset,
            devrelease=devrelease,
        )
        == Version(expected)
    )


@pytest.mark.parametrize(
    "test_input,expected",
    itertools.chain(local_versions),
)
def test_generate_version_local(test_input, expected):
    current_version = test_input[0]
    increment = test_input[1]
    prerelease = test_input[2]
    prerelease_offset = test_input[3]
    devrelease = test_input[4]
    is_local_version = True
    assert (
        generate_version(
            current_version,
            increment=increment,
            prerelease=prerelease,
            prerelease_offset=prerelease_offset,
            devrelease=devrelease,
            is_local_version=is_local_version,
        )
        == Version(expected)
    )
