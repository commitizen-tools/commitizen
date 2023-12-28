import sys
from pathlib import Path
from textwrap import dedent

import pytest
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
    new_tag = bump.create_commit_message(current_version, new_version, message_template)
    assert new_tag == expected


@pytest.mark.parametrize("retry", (True, False))
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_pre_commit_changelog(mocker: MockFixture, freezer, retry):
    freezer.move_to("2022-04-01")
    testargs = ["cz", "bump", "--changelog", "--yes"]
    if retry:
        testargs.append("--retry")
    else:
        pytest.xfail("it will fail because pre-commit will reformat CHANGELOG.md")
    mocker.patch.object(sys, "argv", testargs)
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
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_pre_commit_changelog_fails_always(mocker: MockFixture, freezer, retry):
    freezer.move_to("2022-04-01")
    testargs = ["cz", "bump", "--changelog", "--yes"]
    if retry:
        testargs.append("--retry")
    mocker.patch.object(sys, "argv", testargs)
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
    cmd.run("pre-commit install")
    with pytest.raises(exceptions.BumpCommitFailedError):
        cli.main()


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_build_metadata(mocker: MockFixture, freezer):
    def _add_entry(test_str: str, args: list):
        Path(test_str).write_text("")
        cmd.run("git add -A")
        cmd.run(f'git commit -m "fix: test-{test_str}"')
        cz_args = ["cz", "bump", "--changelog", "--yes"] + args
        mocker.patch.object(sys, "argv", cz_args)
        cli.main()

    freezer.move_to("2024-01-01")

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
