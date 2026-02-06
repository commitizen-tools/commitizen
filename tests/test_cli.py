import os
import subprocess
import sys
import types
from functools import partial

import pytest
from pytest_mock import MockFixture

from commitizen import cli
from commitizen.exceptions import (
    ConfigFileNotFound,
    ExpectedExit,
    InvalidCommandArgumentError,
    NoCommandFoundError,
    NotAGitProjectError,
)
from tests.utils import UtilFixture


@pytest.mark.usefixtures("python_version", "consistent_terminal_output")
def test_no_argv(util: UtilFixture, capsys, file_regression):
    with pytest.raises(ExpectedExit):
        util.run_cli()
    out, err = capsys.readouterr()
    assert out == ""
    file_regression.check(err, extension=".txt")


@pytest.mark.parametrize(
    "arg",
    [
        "--invalid-arg",
        "invalidCommand",
    ],
)
@pytest.mark.usefixtures("python_version", "consistent_terminal_output")
def test_invalid_command(util: UtilFixture, capsys, file_regression, arg):
    with pytest.raises(NoCommandFoundError):
        util.run_cli(arg)
    out, err = capsys.readouterr()
    assert out == ""
    file_regression.check(err, extension=".txt")


def test_cz_config_file_without_correct_file_path(util: UtilFixture, capsys):
    with pytest.raises(ConfigFileNotFound) as excinfo:
        util.run_cli("--config", "./config/pyproject.toml", "example")
    assert "Cannot found the config file" in str(excinfo.value)


def test_cz_with_arg_but_without_command(util: UtilFixture):
    with pytest.raises(NoCommandFoundError) as excinfo:
        util.run_cli("--name", "cz_jira")
    assert "Command is required" in str(excinfo.value)


def test_name(util: UtilFixture, capsys):
    util.run_cli("-n", "cz_jira", "example")
    out, _ = capsys.readouterr()
    assert out.startswith("JRA")


@pytest.mark.usefixtures("tmp_git_project")
def test_name_default_value(util: UtilFixture, capsys):
    util.run_cli("example")
    out, _ = capsys.readouterr()
    assert out.startswith("fix: correct minor typos in code")


def test_ls(util: UtilFixture, capsys):
    util.run_cli("-n", "cz_jira", "ls")
    out, err = capsys.readouterr()

    assert "cz_conventional_commits" in out
    assert isinstance(out, str)


def test_arg_debug(util: UtilFixture):
    util.run_cli("--debug", "info")
    excepthook = sys.excepthook
    # `sys.excepthook` is replaced by a `partial` in `cli.main`
    # it's not a normal function
    assert isinstance(excepthook, partial)
    assert excepthook.keywords.get("debug") is True


def test_commitizen_excepthook(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.commitizen_excepthook(NotAGitProjectError, NotAGitProjectError(), "")

    assert excinfo.type is SystemExit
    assert excinfo.value.code == NotAGitProjectError.exit_code


def test_commitizen_debug_excepthook(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.commitizen_excepthook(
            NotAGitProjectError,
            NotAGitProjectError(),
            "",
            debug=True,
        )

    assert excinfo.type is SystemExit
    assert excinfo.value.code == NotAGitProjectError.exit_code
    assert "NotAGitProjectError" in str(excinfo.traceback[0])


@pytest.mark.skipif(
    os.name == "nt",
    reason="`argcomplete` does not support Git Bash on Windows.",
)
def test_argcomplete_activation():
    """
    This function is testing the one-time activation of argcomplete for
    commitizen only.

    Equivalent to run:
    $ eval "$(register-python-argcomplete pytest)"
    """
    output = subprocess.run(["register-python-argcomplete", "cz"])

    assert output.returncode == 0


def test_commitizen_excepthook_no_raises(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.commitizen_excepthook(
            NotAGitProjectError,
            NotAGitProjectError(),
            "",
            no_raise=[NotAGitProjectError.exit_code],
        )

    assert excinfo.type is SystemExit
    assert excinfo.value.code == 0


@pytest.mark.parametrize(
    ("input_str", "expected_result"),
    [
        pytest.param("1", [1], id="single_code"),
        pytest.param("1,2,3", [1, 2, 3], id="multiple_number_codes"),
        pytest.param(
            "NO_COMMITIZEN_FOUND,NO_COMMITS_FOUND,NO_PATTERN_MAP",
            [1, 3, 5],
            id="string_codes",
        ),
        pytest.param(
            "NO_COMMITIZEN_FOUND,2,NO_COMMITS_FOUND,4",
            [1, 2, 3, 4],
            id="number_and_string_codes",
        ),
        pytest.param(
            "NO_COMMITIZEN_FOUND,2,nothing,4",
            [1, 2, 4],
            id="number_and_string_codes_and_invalid_code",
        ),
    ],
)
def test_parse_no_raise(input_str, expected_result):
    result = cli.parse_no_raise(input_str)
    assert result == expected_result


def test_unknown_args_raises(util: UtilFixture):
    with pytest.raises(InvalidCommandArgumentError) as excinfo:
        util.run_cli("c", "-this_arg_is_not_supported")
    assert "Invalid commitizen arguments were found" in str(excinfo.value)


def test_unknown_args_before_double_dash_raises(util: UtilFixture):
    with pytest.raises(InvalidCommandArgumentError) as excinfo:
        util.run_cli("c", "-this_arg_is_not_supported", "--")
    assert "Invalid commitizen arguments were found before -- separator" in str(
        excinfo.value
    )


def test_commitizen_excepthook_non_commitizen_exception(mocker: MockFixture):
    """Test that commitizen_excepthook delegates to sys.__excepthook__ for non-CommitizenException."""
    # Mock the original excepthook
    mock_original_excepthook = mocker.Mock()
    mocker.patch("commitizen.cli.sys.__excepthook__", mock_original_excepthook)

    # Create a regular exception
    test_exception = ValueError("test error")

    # Call commitizen_excepthook with the regular exception
    cli.commitizen_excepthook(ValueError, test_exception, None)

    # Verify sys.__excepthook__ was called with correct arguments
    mock_original_excepthook.assert_called_once_with(ValueError, test_exception, None)


def test_commitizen_excepthook_non_commitizen_exception_with_traceback(
    mocker: MockFixture,
):
    """Test that commitizen_excepthook handles traceback correctly for non-CommitizenException."""
    # Mock the original excepthook
    mock_original_excepthook = mocker.Mock()
    mocker.patch("commitizen.cli.sys.__excepthook__", mock_original_excepthook)

    # Create a regular exception with a traceback
    test_exception = ValueError("test error")
    test_traceback = mocker.Mock(spec=types.TracebackType)

    # Call commitizen_excepthook with the regular exception and traceback
    cli.commitizen_excepthook(ValueError, test_exception, test_traceback)

    # Verify sys.__excepthook__ was called with correct arguments including traceback
    mock_original_excepthook.assert_called_once_with(
        ValueError, test_exception, test_traceback
    )


def test_commitizen_excepthook_non_commitizen_exception_with_invalid_traceback(
    mocker: MockFixture,
):
    """Test that commitizen_excepthook handles invalid traceback correctly for non-CommitizenException."""
    # Mock the original excepthook
    mock_original_excepthook = mocker.Mock()
    mocker.patch("commitizen.cli.sys.__excepthook__", mock_original_excepthook)

    # Create a regular exception with an invalid traceback
    test_exception = ValueError("test error")
    test_traceback = mocker.Mock()  # Not a TracebackType

    # Call commitizen_excepthook with the regular exception and invalid traceback
    cli.commitizen_excepthook(ValueError, test_exception, test_traceback)

    # Verify sys.__excepthook__ was called with None as traceback
    mock_original_excepthook.assert_called_once_with(ValueError, test_exception, None)
