from unittest import mock

from commitizen import commands


def test_example(config):
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Example(config)()
        write_mock.assert_called_once()


def test_info(config):
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Info(config)()
        write_mock.assert_called_once()


def test_schema(config):
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Schema(config)()
        write_mock.assert_called_once()


def test_list_cz(config):
    with mock.patch("commitizen.out.write") as mocked_write:
        commands.ListCz(config)()
        mocked_write.assert_called_once()
