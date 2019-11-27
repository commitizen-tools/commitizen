import sys

import pytest

from commitizen import cli


def test_sysexit_no_argv():
    with pytest.raises(SystemExit):
        cli.main()


def test_ls(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "ls"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    out, err = capsys.readouterr()

    assert "cz_conventional_commits" in out
    assert isinstance(out, str)


def test_version(mocker):
    testargs = ["cz", "--version"]
    mocker.patch.object(sys, "argv", testargs)
    error_mock = mocker.patch("commitizen.out.error")

    cli.main()

    error_mock.assert_called_once()


def test_check_jira_fails(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="random message for JR-2 #fake_command blah"),
    )
    with pytest.raises(SystemExit):
        cli.main()
    _, err = capsys.readouterr()
    assert "commit validation: failed!" in err


def test_check_jira_succeeds(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JRA-23 correct commit with correct #command etc"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_conventional_commit_succeeds(mocker, capsys):
    testargs = ["cz", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="fix(scope): some commit message"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out
