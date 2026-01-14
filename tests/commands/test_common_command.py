import pytest
from pytest_mock import MockFixture

from commitizen.commands import Example, Info, ListCz, Schema
from tests.utils import UtilFixture


@pytest.mark.parametrize(
    "command",
    [
        "bump",
        "changelog",
        "check",
        "commit",
        "example",
        "info",
        "init",
        "ls",
        "schema",
        "version",
    ],
)
@pytest.mark.usefixtures("python_version", "consistent_terminal_output")
def test_command_shows_description_when_use_help_option(
    capsys,
    file_regression,
    command: str,
    util: UtilFixture,
):
    """Test that the command shows the description when the help option is used.

    Note: If the command description changes, please run `poe test:regen` to regenerate the test files.
    """

    with pytest.raises(SystemExit):
        util.run_cli(command, "--help")

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".txt")


@pytest.mark.parametrize(
    "command",
    [
        Example,
        Info,
        ListCz,
        Schema,
    ],
)
def test_simple_command_call_once(config, mocker: MockFixture, command):
    write_mock = mocker.patch("commitizen.out.write")
    command(config)()
    write_mock.assert_called_once()
