import pytest
import sys
from commitizen import cli, commands

from pytest_mock import MockerFixture

from tests.utils import skip_below_py_3_10


def test_example(config, mocker: MockerFixture):
    write_mock = mocker.patch("commitizen.out.write")
    commands.Example(config)()
    write_mock.assert_called_once()


@skip_below_py_3_10
def test_example_command_shows_description_when_use_help_option(
    mocker: MockerFixture, capsys, file_regression
):
    testargs = ["cz", "example", "--help"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".txt")
