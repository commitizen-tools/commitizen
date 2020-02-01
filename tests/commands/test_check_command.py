import sys

import pytest

from commitizen import cli
from commitizen import commands


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


def test_check_no_conventional_commit(config, mocker, tmpdir):
    with pytest.raises(SystemExit):
        error_mock = mocker.patch("commitizen.out.error")

        tempfile = tmpdir.join("temp_commit_file")
        tempfile.write("no conventional commit")

        check_cmd = commands.Check(
            config=config, arguments={"commit_msg_file": tempfile}
        )
        check_cmd()
        error_mock.assert_called_once()


@pytest.mark.parametrize(
    "commit_msg",
    (
        "feat(lang): added polish language",
        "feat: add polish language",
        "bump: 0.0.1 -> 1.0.0",
    ),
)
def test_check_conventional_commit(commit_msg, config, mocker, tmpdir):
    success_mock = mocker.patch("commitizen.out.success")

    tempfile = tmpdir.join("temp_commit_file")
    tempfile.write(commit_msg)

    check_cmd = commands.Check(config=config, arguments={"commit_msg_file": tempfile})

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_when_commit_file_not_found(config):
    with pytest.raises(FileNotFoundError):
        commands.Check(config=config, arguments={"commit_msg_file": ""})()
