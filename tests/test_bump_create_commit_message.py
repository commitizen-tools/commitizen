import sys
from pathlib import Path
from textwrap import dedent

import pytest

from commitizen import bump, cmd, exceptions
from tests.utils import UtilFixture

conversion = [
    (
        ("1.2.3", "1.3.0", "bump: $current_version -> $new_version [skip ci]"),
        "bump: 1.2.3 -> 1.3.0 [skip ci]",
    ),
    (("1.2.3", "1.3.0", None), "bump: version 1.2.3 → 1.3.0"),
    (("1.2.3", "1.3.0", "release $new_version"), "release 1.3.0"),
]


@pytest.mark.parametrize("test_input,expected", conversion)
def test_create_tag(test_input, expected):
    current_version, new_version, message_template = test_input
    new_tag = bump.create_commit_message(current_version, new_version, message_template)
    assert new_tag == expected


@pytest.mark.parametrize(
    "retry",
    (
        pytest.param(
            True,
            marks=pytest.mark.skipif(
                sys.version_info >= (3, 13),
                reason="mirrors-prettier is not supported with Python 3.13 or higher",
            ),
        ),
        False,
    ),
)
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_pre_commit_changelog(util: UtilFixture, retry):
    util.freezer.move_to("2022-04-01")
    bump_args = ["bump", "--changelog", "--yes"]
    if retry:
        bump_args.append("--retry")
    else:
        pytest.xfail("it will fail because pre-commit will reformat CHANGELOG.md")
    # Configure prettier as a pre-commit hook
    Path(".pre-commit-config.yaml").write_text(
        dedent(
            """\
            repos:
              - repo: https://github.com/pre-commit/mirrors-prettier
                rev: v3.0.3
                hooks:
                - id: prettier
                  stages: [commit]
            """
        )
    )
    # Prettier inherits editorconfig
    Path(".editorconfig").write_text(
        dedent(
            """\
            [*]
            indent_size = 4
            """
        )
    )
    cmd.run("git add -A")
    cmd.run('git commit -m "fix: _test"')
    cmd.run("prek install")
    util.run_cli(*bump_args)
    # Pre-commit fixed last line adding extra indent and "\" char
    assert Path("CHANGELOG.md").read_text() == dedent(
        """\
        ## 0.1.1 (2022-04-01)

        ### Fix

        -   \\_test
        """
    )


@pytest.mark.parametrize("retry", (True, False))
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_pre_commit_changelog_fails_always(util: UtilFixture, retry):
    util.freezer.move_to("2022-04-01")
    bump_args = ["bump", "--changelog", "--yes"]
    if retry:
        bump_args.append("--retry")
    Path(".pre-commit-config.yaml").write_text(
        dedent(
            """\
            repos:
              - repo: local
                hooks:
                - id: forbid-changelog
                  name: changelogs are forbidden
                  entry: changelogs are forbidden
                  language: fail
                  files: CHANGELOG.md
            """
        )
    )
    cmd.run("git add -A")
    cmd.run('git commit -m "feat: forbid changelogs"')
    cmd.run("prek install")
    with pytest.raises(exceptions.BumpCommitFailedError):
        util.run_cli(*bump_args)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_build_metadata(util: UtilFixture):
    def _add_entry(test_str: str, args: list):
        Path(test_str).write_text("")
        cmd.run("git add -A")
        cmd.run(f'git commit -m "fix: test-{test_str}"')
        cz_args = ["bump", "--changelog", "--yes"] + args
        util.run_cli(*cz_args)

    util.freezer.move_to("2024-01-01")

    _add_entry("a", ["--build-metadata", "a.b.c"])
    _add_entry("b", [])
    _add_entry("c", ["--build-metadata", "alongmetadatastring"])
    _add_entry("d", [])

    # Pre-commit fixed last line adding extra indent and "\" char
    assert Path("CHANGELOG.md").read_text() == dedent(
        """\
        ## 0.1.4 (2024-01-01)

        ### Fix

        - test-d

        ## 0.1.3+alongmetadatastring (2024-01-01)

        ### Fix

        - test-c

        ## 0.1.2 (2024-01-01)

        ### Fix

        - test-b

        ## 0.1.1+a.b.c (2024-01-01)

        ### Fix

        - test-a
        """
    )
