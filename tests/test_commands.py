import os
from unittest import mock

import pytest

from commitizen import cmd, commands, defaults
from commitizen.cz.exceptions import CzException

config = {"name": defaults.name}


@pytest.fixture
def staging_is_clean(mocker):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = False


@pytest.mark.usefixtures("staging_is_clean")
def test_commit(mocker):
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
    commit_mock.return_value = cmd.Command("success", "", "", "")
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {})()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_fails_no_backup(mocker):
    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "")

    with pytest.raises(SystemExit):
        commands.Commit(config, {"retry": True})()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_works(mocker):
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
    commit_mock.return_value = cmd.Command("", "error", "", "")
    error_mock = mocker.patch("commitizen.out.error")

    with pytest.raises(SystemExit):
        commit_cmd = commands.Commit(config, {})
        temp_file = commit_cmd.temp_file
        commit_cmd()

    prompt_mock.assert_called_once()
    error_mock.assert_called_once()
    assert os.path.isfile(temp_file)

    # Previous commit failed, so retry should pick up the backup commit
    # commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "")
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {"retry": True})()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21")
    prompt_mock.assert_called_once()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


def test_commit_when_nothing_to_commit(mocker):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = True

    with pytest.raises(SystemExit) as err:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    assert err.value.code == commands.commit.NOTHING_TO_COMMIT


def test_commit_when_customized_expected_raised(mocker, capsys):
    _err = ValueError()
    _err.__context__ = CzException("This is the root custom err")
    git_mock = mocker.patch("commitizen.git.is_staging_clean")
    git_mock.return_value = False
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.side_effect = _err

    with pytest.raises(SystemExit) as err:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    assert err.value.code == commands.commit.CUSTOM_ERROR

    # Assert only the content in the formatted text
    captured = capsys.readouterr()
    assert "This is the root custom err" in captured.err


def test_example():
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Example(config)()
        write_mock.assert_called_once()


def test_info():
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Info(config)()
        write_mock.assert_called_once()


def test_schema():
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Schema(config)()
        write_mock.assert_called_once()


def test_list_cz():
    with mock.patch("commitizen.out.write") as mocked_write:

        commands.ListCz(config)()
        mocked_write.assert_called_once()


def test_version():
    with mock.patch("commitizen.out.write") as mocked_write:

        commands.Version(config)()
        mocked_write.assert_called_once()
