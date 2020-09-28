import sys

import pytest

from commitizen import cli, cmd, commands, git
from commitizen.exceptions import InvalidCommandArgumentError
from tests.utils import create_file_and_commit


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_undo_commit(config, mocker):
    create_file_and_commit("feat: new file")
    # We can not revert the first commit, thus we commit twice.
    create_file_and_commit("feat: extra file")

    testargs = ["cz", "undo", "--commit"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    commits = git.get_commits()

    assert len(commits) == 1


def _execute_command(mocker, testargs):
    mocker.patch.object(sys, "argv", testargs)
    cli.main()


def _undo_bump(mocker, tag_num: int = 0):
    testargs = ["cz", "undo", "--bump"]
    tags = git.get_tags()
    print(tags)
    _execute_command(mocker, testargs)

    tags = git.get_tags()
    print(tags)
    print(git.get_commits())

    assert len(tags) == tag_num


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_undo_bump(config, mocker):
    # MINOR
    create_file_and_commit("feat: new file")
    _execute_command(mocker, ["cz", "bump", "--yes"])
    _undo_bump(mocker)

    # PATCH
    create_file_and_commit("feat: new file")
    _execute_command(mocker, ["cz", "bump", "--yes"])

    create_file_and_commit("fix: username exception")
    _execute_command(mocker, ["cz", "bump"])
    _undo_bump(mocker, 1)

    # PRERELEASE
    create_file_and_commit("feat: location")
    _execute_command(mocker, ["cz", "bump", "--prerelease", "alpha"])
    _undo_bump(mocker, 1)

    # # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    create_file_and_commit("feat: location")
    _execute_command(mocker, ["cz", "bump", "--prerelease", "alpha"])
    _execute_command(mocker, ["cz", "bump"])
    _undo_bump(mocker, 2)

    # MAJOR
    create_file_and_commit(
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported"
    )
    _execute_command(mocker, ["cz", "bump"])
    _undo_bump(mocker, 2)
