import sys

import pytest
from pytest_mock import MockFixture

from commitizen import cli
from commitizen.commands import Example, Info, ListCz, Schema


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
@pytest.mark.usefixtures("python_version")
def test_command_shows_description_when_use_help_option(
    mocker: MockFixture,
    capsys,
    file_regression,
    monkeypatch: pytest.MonkeyPatch,
    command: str,
):
    """Test that the command shows the description when the help option is used.

    Note: If the command description changes, please run `poe test:regen` to regenerate the test files.
    """
    # Force consistent terminal output
    monkeypatch.setenv("COLUMNS", "80")
    monkeypatch.setenv("TERM", "dumb")
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.setenv("LANG", "C")
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("PAGER", "cat")

    testargs = ["cz", command, "--help"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

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
