import os
import sys
from pathlib import Path
from textwrap import dedent

import pytest
from packaging.version import Version
from pytest_mock import MockFixture

from commitizen import bump, cli, cmd, exceptions

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
    new_tag = bump.create_commit_message(
        Version(current_version), Version(new_version), message_template
    )
    assert new_tag == expected


@pytest.mark.parametrize("retry", (True, False))
def test_bump_pre_commit_changelog(
    tmp_commitizen_project, mocker: MockFixture, freezer, retry
):
    freezer.move_to("2022-04-01")
    testargs = ["cz", "bump", "--changelog", "--yes"]
    if retry:
        testargs.append("--retry")
    else:
        pytest.xfail("it will fail because pre-commit will reformat CHANGELOG.md")
    mocker.patch.object(sys, "argv", testargs)
    with tmp_commitizen_project.as_cwd():
        # Configure prettier as a pre-commit hook
        Path(".pre-commit-config.yaml").write_text(
            """
            repos:
              - repo: https://github.com/pre-commit/mirrors-prettier
                rev: v2.6.2
                hooks:
                - id: prettier
                  stages: [commit]
            """
        )
        # Prettier inherits editorconfig
        Path(".editorconfig").write_text(
            """
            [*]
            indent_size = 4
            """
        )
        cmd.run("git add -A")
        if os.name == "nt":
            cmd.run('git commit -m "fix: _test"')
        else:
            cmd.run("git commit -m 'fix: _test'")
        cmd.run("pre-commit install")
        cli.main()
        # Pre-commit fixed last line adding extra indent and "\" char
        assert Path("CHANGELOG.md").read_text() == dedent(
            """\
            ## 0.1.1 (2022-04-01)

            ### Fix

            -   \\_test
            """
        )


@pytest.mark.parametrize("retry", (True, False))
def test_bump_pre_commit_changelog_fails_always(
    tmp_commitizen_project, mocker: MockFixture, freezer, retry
):
    freezer.move_to("2022-04-01")
    testargs = ["cz", "bump", "--changelog", "--yes"]
    if retry:
        testargs.append("--retry")
    mocker.patch.object(sys, "argv", testargs)
    with tmp_commitizen_project.as_cwd():
        Path(".pre-commit-config.yaml").write_text(
            """
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
        cmd.run("git add -A")
        if os.name == "nt":
            cmd.run('git commit -m "feat: forbid changelogs"')
        else:
            cmd.run("git commit -m 'feat: forbid changelogs'")
        cmd.run("pre-commit install")
        with pytest.raises(exceptions.BumpCommitFailedError):
            cli.main()
