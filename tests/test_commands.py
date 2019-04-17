# import pytest
from unittest import mock
from commitizen import defaults, commands, cmd

config = {"name": defaults.name}


def test_commit(mocker):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "")
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config)()
    success_mock.assert_called_once()


def test_example():
    with mock.patch("commitizen.out.write") as write_mock:
        # mock_cz = mock.Mock()
        # mocked_factory.return_value = mock_cz
        commands.Example(config)()
        write_mock.assert_called_once()

        # mocked_factory.assert_called_once()
        # mock_cz.show_example.assert_called_once()


def test_info():
    with mock.patch("commitizen.factory.commiter_factory") as mocked_factory:
        mock_cz = mock.Mock()
        mocked_factory.return_value = mock_cz
        commands.Info(config)()

        mocked_factory.assert_called_once()
        mock_cz.show_info.assert_called_once()


def test_schema():
    with mock.patch("commitizen.factory.commiter_factory") as mocked_factory:
        mock_cz = mock.Mock()
        mocked_factory.return_value = mock_cz
        commands.Schema(config)()

        mocked_factory.assert_called_once()
        mock_cz.show_schema.assert_called_once()


def test_list_cz():
    with mock.patch("commitizen.out.write") as mocked_write:

        commands.ListCz(config)()
        mocked_write.assert_called_once()
