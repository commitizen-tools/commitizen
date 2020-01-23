import sys

import pytest

from commitizen import cli
from tests.utils import create_file_and_commit


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changlog_on_empty_project(mocker):
    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(SystemExit):
        cli.main()


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changlog_from_start(mocker, capsys):
    create_file_and_commit("feat: new file")
    create_file_and_commit("refactor: not in changelog")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    assert out == "# CHANGELOG\n\n## Unreleased\n### feat\n- new file\n\n\n"


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changlog_from_version_zero_point_two(mocker, capsys):
    create_file_and_commit("feat: new file")
    create_file_and_commit("refactor: not in changelog")

    # create tag
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    capsys.readouterr()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: after 0.2")

    testargs = ["cz", "changelog", "--start-rev", "0.2.0", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    assert out == "# CHANGELOG\n\n## Unreleased\n### feat\n- after 0.2\n- after 0.2.0\n\n\n"


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changlog_with_unsupported_cz(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(SystemExit):
        cli.main()
    out, err = capsys.readouterr()
    assert "'cz_jira' rule does not support changelog" in err
