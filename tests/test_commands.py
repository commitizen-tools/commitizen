# import pytest
from unittest import mock
from commitizen import defaults, commands

config = {"name": defaults.name}


def test_commit():
    with mock.patch("commitizen.factory.commiter_factory") as mocked_factory:
        mock_cz = mock.Mock()
        mocked_factory.return_value = mock_cz
        commands.Commit(config)()

        mocked_factory.assert_called_once()
        mock_cz.run.assert_called_once()


def test_example():
    with mock.patch("commitizen.factory.commiter_factory") as mocked_factory:
        mock_cz = mock.Mock()
        mocked_factory.return_value = mock_cz
        commands.Example(config)()

        mocked_factory.assert_called_once()
        mock_cz.show_example.assert_called_once()


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
