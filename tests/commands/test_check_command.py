import sys

import pytest

from commitizen import cli


def test_check_jira_fails(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="random message for J-2 #fake_command blah"),
    )
    with pytest.raises(SystemExit):
        cli.main()
    _, err = capsys.readouterr()
    assert "commit validation: failed!" in err


def test_check_jira_command_after_issue_one_space(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JR-23 #command some arguments etc"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_jira_command_after_issue_two_spaces(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JR-2  #command some arguments etc"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_jira_text_between_issue_and_command(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JR-234 some text #command some arguments etc"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_jira_multiple_commands(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JRA-23 some text #command1 args #command2 args"),
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
