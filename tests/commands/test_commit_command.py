import os
import sys

import pytest
from pytest_mock import MockFixture
from unittest.mock import ANY

from commitizen import cli, cmd, commands
from commitizen.cz.exceptions import CzException
from commitizen.cz.utils import get_backup_file_path
from commitizen.exceptions import (
    CommitError,
    CommitMessageLengthExceededError,
    CustomError,
    DryRunExit,
    NoAnswersError,
    NoCommitBackupError,
    NotAGitProjectError,
    NotAllowed,
    NothingToCommitError,
)


@pytest.fixture
def staging_is_clean(mocker: MockFixture, tmp_git_project):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = False
    return tmp_git_project


@pytest.fixture
def backup_file(tmp_git_project):
    with open(get_backup_file_path(), "w") as backup_file:
        backup_file.write("backup commit")


@pytest.mark.usefixtures("staging_is_clean")
def test_commit(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {})()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_backup_on_failure(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #21",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("", "error", b"", b"", 9)
    error_mock = mocker.patch("commitizen.out.error")

    with pytest.raises(CommitError):
        commit_cmd = commands.Commit(config, {})
        temp_file = commit_cmd.temp_file
        commit_cmd()

    prompt_mock.assert_called_once()
    error_mock.assert_called_once()
    assert os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_fails_no_backup(config, mocker: MockFixture):
    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)

    with pytest.raises(NoCommitBackupError) as excinfo:
        commands.Commit(config, {"retry": True})()

    assert NoCommitBackupError.message in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_works(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    commit_cmd = commands.Commit(config, {"retry": True})
    temp_file = commit_cmd.temp_file
    commit_cmd()

    commit_mock.assert_called_with("backup commit", args="")
    prompt_mock.assert_not_called()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_after_failure_no_backup(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #21",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    config.settings["retry_after_failure"] = True
    commands.Commit(config, {})()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21", args="")
    prompt_mock.assert_called_once()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_after_failure_works(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    config.settings["retry_after_failure"] = True
    commit_cmd = commands.Commit(config, {})
    temp_file = commit_cmd.temp_file
    commit_cmd()

    commit_mock.assert_called_with("backup commit", args="")
    prompt_mock.assert_not_called()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_after_failure_with_no_retry_works(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #21",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    config.settings["retry_after_failure"] = True
    commit_cmd = commands.Commit(config, {"no_retry": True})
    temp_file = commit_cmd.temp_file
    commit_cmd()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21", args="")
    prompt_mock.assert_called_once()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_dry_run_option(config, mocker: MockFixture):
    prompt_mock = mocker = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #57",
        "footer": "",
    }

    with pytest.raises(DryRunExit):
        commit_cmd = commands.Commit(config, {"dry_run": True})
        commit_cmd()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_write_message_to_file_option(
    config, tmp_path, mocker: MockFixture
):
    tmp_file = tmp_path / "message"

    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {"write_message_to_file": tmp_file})()
    success_mock.assert_called_once()
    assert tmp_file.exists()
    assert tmp_file.read_text() == "feat: user created"


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_invalid_write_message_to_file_option(
    config, tmp_path, mocker: MockFixture
):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    with pytest.raises(NotAllowed):
        commit_cmd = commands.Commit(config, {"write_message_to_file": tmp_path})
        commit_cmd()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_signoff_option(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {"signoff": True})()

    commit_mock.assert_called_once_with(ANY, args="-- -s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_always_signoff_enabled(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    config.settings["always_signoff"] = True
    commands.Commit(config, {})()

    commit_mock.assert_called_once_with(ANY, args="-- -s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("tmp_git_project")
def test_commit_when_nothing_to_commit(config, mocker: MockFixture):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = True

    with pytest.raises(NothingToCommitError) as excinfo:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    assert "No files added to staging!" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_customized_expected_raised(config, mocker: MockFixture, capsys):
    _err = ValueError()
    _err.__context__ = CzException("This is the root custom err")
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.side_effect = _err

    with pytest.raises(CustomError) as excinfo:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    # Assert only the content in the formatted text
    assert "This is the root custom err" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_non_customized_expected_raised(
    config, mocker: MockFixture, capsys
):
    _err = ValueError()
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.side_effect = _err

    with pytest.raises(ValueError):
        commit_cmd = commands.Commit(config, {})
        commit_cmd()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_no_user_answer(config, mocker: MockFixture, capsys):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = None

    with pytest.raises(NoAnswersError):
        commit_cmd = commands.Commit(config, {})
        commit_cmd()


def test_commit_in_non_git_project(tmpdir, config):
    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            commands.Commit(config, {})


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_all_option(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")
    add_mock = mocker.patch("commitizen.git.add")
    commands.Commit(config, {"all": True})()
    add_mock.assert_called()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_extra_args(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")
    commands.Commit(config, {"extra_cli_args": "-- -extra-args1 -extra-arg2"})()
    commit_mock.assert_called_once_with(ANY, args="-- -extra-args1 -extra-arg2")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_message_length_limit(config, mocker: MockFixture):
    prompt_mock = mocker.patch("questionary.prompt")
    prefix = "feat"
    subject = "random subject"
    message_length = len(prefix) + len(": ") + len(subject)
    prompt_mock.return_value = {
        "prefix": prefix,
        "subject": subject,
        "scope": "",
        "is_breaking_change": False,
        "body": "random body",
        "footer": "random footer",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {"message_length_limit": message_length})()
    success_mock.assert_called_once()

    with pytest.raises(CommitMessageLengthExceededError):
        commands.Commit(config, {"message_length_limit": message_length - 1})()


def test_commit_command_shows_description_when_use_help_option(
    mocker: MockFixture, capsys, file_regression
):
    testargs = ["cz", "commit", "--help"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".txt")
