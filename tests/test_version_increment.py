"""Tests for semantic-version increment ordering and extraction helpers."""

import re

import pytest

from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.version_increment import VersionIncrement

NONE_INCREMENT_CC = [
    "docs(README): motivation",
    "ci: added travis",
    "performance. Remove or disable the reimplemented linters",
    "refactor that how this line starts",
]

PATCH_INCREMENTS_CC = [
    "fix(setup.py): future is now required for every python version",
    "docs(README): motivation",
]

MINOR_INCREMENTS_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
    "perf: app is much faster",
    "refactor: app is much faster",
]

MAJOR_INCREMENTS_BREAKING_CHANGE_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "BREAKING CHANGE: `extends` key in config file is now used for extending other config files",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_BREAKING_CHANGE_ALT_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "BREAKING-CHANGE: `extends` key in config file is now used for extending other config files",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_EXCLAMATION_CC = [
    "feat(cli)!: added version",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_EXCLAMATION_CC_SAMPLE_2 = [
    "feat(pipeline)!: some text with breaking change"
]

MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_CC = [
    "chore!: drop support for Python 3.9",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_WITH_SCOPE_CC = [
    "chore(deps)!: drop support for Python 3.9",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

PATCH_INCREMENTS_SVE = ["readme motivation PATCH", "fix setup.py PATCH"]

MINOR_INCREMENTS_SVE = [
    "readme motivation PATCH",
    "fix setup.py PATCH",
    "added version to cli MINOR",
]

MAJOR_INCREMENTS_SVE = [
    "readme motivation PATCH",
    "fix setup.py PATCH",
    "added version to cli MINOR",
    "extends key is used for other config files MAJOR",
]

SEMANTIC_VERSION_PATTERN = r"(MAJOR|MINOR|PATCH)"
SEMANTIC_VERSION_MAP = {"MAJOR": "MAJOR", "MINOR": "MINOR", "PATCH": "PATCH"}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("MAJOR", VersionIncrement.MAJOR),
        ("MINOR", VersionIncrement.MINOR),
        ("PATCH", VersionIncrement.PATCH),
        ("NONE", VersionIncrement.NONE),
        ("not_a_valid_name", VersionIncrement.NONE),
        (None, VersionIncrement.NONE),
        (123, VersionIncrement.NONE),
    ],
)
def test_version_increment_from_value(
    value: object, expected: VersionIncrement
) -> None:
    """Unknown values fall back to NONE instead of raising."""
    assert VersionIncrement.from_value(value) == expected


def test_version_increment_str() -> None:
    """String conversion preserves the legacy enum names."""
    assert str(VersionIncrement.PATCH) == "PATCH"


def test_version_increment_comparison_order() -> None:
    """The enum provides semantic ordering instead of string ordering."""
    assert VersionIncrement.NONE < VersionIncrement.PATCH
    assert VersionIncrement.PATCH < VersionIncrement.MINOR
    assert VersionIncrement.MINOR < VersionIncrement.MAJOR


def test_version_increment_max_uses_semantic_order() -> None:
    """max() chooses the highest semantic increment across mixed values."""
    assert (
        max(
            [
                VersionIncrement.PATCH,
                VersionIncrement.MAJOR,
                VersionIncrement.MINOR,
                VersionIncrement.NONE,
            ]
        )
        == VersionIncrement.MAJOR
    )


@pytest.mark.parametrize(
    ("messages", "expected"),
    [
        (PATCH_INCREMENTS_CC, VersionIncrement.PATCH),
        (MINOR_INCREMENTS_CC, VersionIncrement.MINOR),
        (MAJOR_INCREMENTS_BREAKING_CHANGE_CC, VersionIncrement.MAJOR),
        (MAJOR_INCREMENTS_BREAKING_CHANGE_ALT_CC, VersionIncrement.MAJOR),
        (MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_CC, VersionIncrement.MAJOR),
        (
            MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_WITH_SCOPE_CC,
            VersionIncrement.MAJOR,
        ),
        (MAJOR_INCREMENTS_EXCLAMATION_CC, VersionIncrement.MAJOR),
        (MAJOR_INCREMENTS_EXCLAMATION_CC_SAMPLE_2, VersionIncrement.MAJOR),
        (NONE_INCREMENT_CC, VersionIncrement.NONE),
    ],
)
def test_get_highest_by_messages_for_conventional_commits(
    messages: list[str], expected: VersionIncrement
) -> None:
    """Conventional-commit bump detection matches the existing behavior."""
    assert (
        VersionIncrement.get_highest_by_messages(
            messages,
            ConventionalCommitsCz.bump_pattern,
            ConventionalCommitsCz.bump_map,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("messages", "expected"),
    [
        (PATCH_INCREMENTS_SVE, VersionIncrement.PATCH),
        (MINOR_INCREMENTS_SVE, VersionIncrement.MINOR),
        (MAJOR_INCREMENTS_SVE, VersionIncrement.MAJOR),
    ],
)
def test_get_highest_by_messages_for_semantic_tokens(
    messages: list[str], expected: VersionIncrement
) -> None:
    """Custom bump maps continue to work with the shared extraction helpers."""
    assert (
        VersionIncrement.get_highest_by_messages(
            messages,
            SEMANTIC_VERSION_PATTERN,
            SEMANTIC_VERSION_MAP,
        )
        == expected
    )


def test_get_highest_by_messages_returns_none_for_empty_input() -> None:
    """Empty inputs preserve the existing no-increment behavior explicitly."""
    assert (
        VersionIncrement.get_highest_by_messages(
            [],
            ConventionalCommitsCz.bump_pattern,
            ConventionalCommitsCz.bump_map,
        )
        == VersionIncrement.NONE
    )


def test_from_message_uses_highest_matching_line() -> None:
    """A multiline commit message keeps the highest line-level increment."""
    message = (
        "feat(api): add endpoint\n\nBREAKING CHANGE: remove the legacy response body"
    )

    assert (
        VersionIncrement.from_message(
            message,
            ConventionalCommitsCz.bump_pattern,
            ConventionalCommitsCz.bump_map,
        )
        == VersionIncrement.MAJOR
    )


def test_get_highest_by_messages_supports_custom_none_mapping() -> None:
    """A matched custom rule can still explicitly opt out of bumping."""
    assert (
        VersionIncrement.get_highest_by_messages(
            ["docs: update guide"],
            r"^(docs)",
            {"docs": None},
        )
        == VersionIncrement.NONE
    )


def test_get_highest_by_messages_rejects_string_none_mapping() -> None:
    """The string NONE remains invalid at the bump-map computation boundary."""
    with pytest.raises(ValueError, match="NONE"):
        VersionIncrement.get_highest_by_messages(
            ["docs: update guide"],
            r"^(docs)",
            {"docs": "NONE"},
        )


def test_from_message_stops_after_major_match() -> None:
    """A major match on one line shields later invalid lines in that message."""
    assert (
        VersionIncrement.from_message(
            "break: api\n\noops: typo",
            r"^(break|oops)",
            {"break": "MAJOR", "oops": "MINORR"},
        )
        == VersionIncrement.MAJOR
    )


def test_get_highest_by_messages_raises_for_invalid_bump_map_value() -> None:
    """A matched custom bump-map value must fail instead of becoming NONE."""
    with pytest.raises(ValueError, match="MINORR"):
        VersionIncrement.get_highest_by_messages(
            ["new: add endpoint"],
            r"^(new)",
            {"new": "MINORR"},
        )


def test_get_highest_by_messages_compiles_pattern_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scanning many messages reuses one compiled bump pattern."""
    compile_calls = 0
    original_compile = re.compile

    def counted_compile(pattern: str, flags: int = 0) -> re.Pattern[str]:
        """Record each pattern compilation while preserving regex behavior."""
        nonlocal compile_calls
        compile_calls += 1
        return original_compile(pattern, flags)

    monkeypatch.setattr("commitizen.version_increment.re.compile", counted_compile)

    increment = VersionIncrement.get_highest_by_messages(
        [
            "fix: correct typo",
            "feat(api): add endpoint\n\nBREAKING CHANGE: remove fallback",
        ],
        ConventionalCommitsCz.bump_pattern,
        ConventionalCommitsCz.bump_map,
    )

    assert increment == VersionIncrement.MAJOR
    assert compile_calls == 1
