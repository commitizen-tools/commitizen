import os
from unittest import mock

import pytest

from commitizen import cmd, commands, defaults

config = {"name": defaults.name}


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


def test_commit_retry_fails_no_backup(mocker):
    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "")

    with pytest.raises(SystemExit):
        commands.Commit(config, {"retry": True})()


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
