from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from commitizen.changelog import Metadata
from commitizen.changelog_formats.restructuredtext import RestructuredText
from commitizen.config.base_config import BaseConfig

if TYPE_CHECKING:
    from _pytest.mark.structures import ParameterSet


CASES: list[ParameterSet] = []


def case(
    id: str,
    content: str,
    latest_version: str | None = None,
    latest_version_position: int | None = None,
    unreleased_start: int | None = None,
    unreleased_end: int | None = None,
):
    CASES.append(
        pytest.param(
            dedent(content).strip(),
            Metadata(
                latest_version=latest_version,
                latest_version_position=latest_version_position,
                unreleased_start=unreleased_start,
                unreleased_end=unreleased_end,
            ),
            id=id,
        )
    )


case(
    "underlined title with intro and unreleased section",
    """
    Changelog
    #########

    All notable changes to this project will be documented in this file.

    The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`,
    and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`.

    Unreleased
    ==========
    * Start using "changelog" over "change log" since it's the common usage.

    1.0.0 - 2017-06-20
    ==================
    Added
    -----
    * New visual identity by `@tylerfortune8 <https://github.com/tylerfortune8>`.
    * Version navigation.
    """,
    latest_version="1.0.0",
    latest_version_position=12,
    unreleased_start=8,
    unreleased_end=12,
)

case(
    "unreleased section without preamble",
    """
    Unreleased
    ==========
    * Start using "changelog" over "change log" since it's the common usage.

    1.2.0
    =====
    """,
    latest_version="1.2.0",
    latest_version_position=4,
    unreleased_start=0,
    unreleased_end=4,
)

case(
    "basic underlined titles with v-prefixed version",
    """
    Unreleased
    ==========

    v1.0.0
    ======
    """,
    latest_version="1.0.0",
    latest_version_position=3,
    unreleased_start=0,
    unreleased_end=3,
)

case(
    "intermediate section in unreleased",
    """
    Unreleased
    ==========

    intermediate
    ------------

    1.0.0
    =====
    """,
    latest_version="1.0.0",
    latest_version_position=6,
    unreleased_start=0,
    unreleased_end=6,
)

case(
    "weird section with different level than versions",
    """
    Unreleased
    ##########

    1.0.0
    =====
    """,
    latest_version="1.0.0",
    latest_version_position=3,
    unreleased_start=0,
    unreleased_end=3,
)

case(
    "overlined title without release and intro",
    """
    ==========
    Unreleased
    ==========
    * Start using "changelog" over "change log" since it's the common usage.
    """,
    unreleased_start=0,
    unreleased_end=4,
)

case(
    "underlined title with date",
    """
    1.0.0 - 2017-06-20
    ==================
    """,
    latest_version="1.0.0",
    latest_version_position=0,
)


UNDERLINED_TITLES = (
    """
    title
    =====
    """,
    """
    title
    ======
    """,
    """
    title
    #####
    """,
    """
    title
    .....
    """,
    """
    title
    !!!!!
    """,
)

NOT_UNDERLINED_TITLES = (
    """
    title
    =.=.=
    """,
    """
    title
    ====
    """,
    """
    title
    aaaaa
    """,
    """
    title

    """,
)


OVERLINED_TITLES = (
    """
    =====
    title
    =====
    """,
    """
    ======
    title
    ======
    """,
    """
    #####
    title
    #####
    """,
    """
    .....
    title
    .....
    """,
)

NOT_OVERLINED_TITLES = (
    """
    ====
    title
    =====
    """,
    """
    =====
    title
    ====
    """,
    """
    ====
    title
    ====
    """,
    """
    =====
    title
    #####
    """,
    """
    #####
    title
    =====
    """,
    """
    =.=.=
    title
    =====
    """,
    """
    =====
    title
    =.=.=
    """,
    """

    title
    =====
    """,
    """
    =====
    title

    """,
    """
    aaaaa
    title
    aaaaa
    """,
)


@pytest.fixture
def format(config: BaseConfig) -> RestructuredText:
    return RestructuredText(config)


@pytest.mark.parametrize("content, expected", CASES)
def test_get_matadata(
    tmp_path: Path, format: RestructuredText, content: str, expected: Metadata
):
    changelog = tmp_path / format.default_changelog_file
    changelog.write_text(content)

    assert format.get_metadata(str(changelog)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [(text, True) for text in UNDERLINED_TITLES]
    + [(text, False) for text in NOT_UNDERLINED_TITLES],
)
def test_is_underlined_title(format: RestructuredText, text: str, expected: bool):
    _, first, second = dedent(text).splitlines()
    assert format.is_underlined_title(first, second) is expected


@pytest.mark.parametrize(
    "text, expected",
    [(text, True) for text in OVERLINED_TITLES]
    + [(text, False) for text in NOT_OVERLINED_TITLES],
)
def test_is_overlined_title(format: RestructuredText, text: str, expected: bool):
    _, first, second, third = dedent(text).splitlines()

    assert format.is_overlined_title(first, second, third) is expected
