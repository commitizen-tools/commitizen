import sys

import pytest

from commitizen import cli, cmd, git
from tests.utils import create_file_and_commit


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command(mocker):
    # MINOR
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    # PATCH
    create_file_and_commit("fix: username exception")

    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.1")
    assert tag_exists is True

    # PRERELEASE
    create_file_and_commit("feat: location")

    testargs = ["cz", "bump", "--prerelease", "alpha"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.3.0a0")
    assert tag_exists is True

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.3.0")
    assert tag_exists is True

    # MAJOR
    create_file_and_commit(
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported"
    )

    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("1.0.0")
    assert tag_exists is True


def test_bump_when_bumpping_is_not_support(mocker, capsys, tmpdir):
    with tmpdir.as_cwd():
        with open("./pyproject.toml", "w") as f:
            f.write("[tool.commitizen]\n" 'version="0.1.0"')

        cmd.run("git init")
        create_file_and_commit(
            "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported"
        )

        testargs = ["cz", "-n", "cz_jira", "bump", "--yes"]
        mocker.patch.object(sys, "argv", testargs)

        with pytest.raises(SystemExit):
            cli.main()

        _, err = capsys.readouterr()
        assert "'cz_jira' rule does not support bump" in err


@pytest.mark.usefixtures("tmp_git_project")
def test_bump_is_not_specify(mocker, capsys):
    mocker.patch.object(sys, "argv", ["cz", "bump"])

    with pytest.raises(SystemExit):
        cli.main()

    expected_error_message = (
        "[NO_VERSION_SPECIFIED]\n"
        "Check if current version is specified in config file, like:\n"
        "version = 0.4.3\n"
    )

    _, err = capsys.readouterr()
    assert expected_error_message in err


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_when_not_new_commit(mocker, capsys):
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(SystemExit):
        cli.main()

    expected_error_message = "[NO_COMMITS_FOUND]\n" "No new commits found."
    _, err = capsys.readouterr()
    assert expected_error_message in err
