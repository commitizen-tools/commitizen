import sys

import pytest
from pytest_mock import MockFixture

from commitizen import cli
from commitizen.commands import Example, Info, ListCz, Schema


def py_version_tag() -> str:
    """Used in file regression tests to differentiate between Python versions."""
    return f"py{sys.version_info.major}_{sys.version_info.minor}"


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
def test_command_shows_description_when_use_help_option(
    mocker: MockFixture,
    capsys,
    file_regression,
    stable_cli_env,
    command: str,
):
    """Test that the command shows the description when the help option is used.

    Note: If the command description changes, please run `tox -- tests/commands/test_common_command.py --regen-all` to regenerate the test files.
    """
    testargs = ["cz", command, "--help"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()

    # The output message of argparse is different between Python versions, especially below 3.13 and above 3.13.
    file_regression.check(
        out,
        extension=".txt",
        basename=f"test_command_shows_description_when_use_help_option_{command}_{py_version_tag()}",
    )


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
