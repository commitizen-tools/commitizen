import os
import subprocess
import sys
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


def test_sysexit_no_argv(mocker: MockFixture, capsys):
    testargs = ["cz"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(ExpectedExit):
        cli.main()
        out, _ = capsys.readouterr()
        assert out.startswith("usage")


def test_cz_config_file_without_correct_file_path(mocker: MockFixture, capsys):
    testargs = ["cz", "--config", "./config/pyproject.toml", "example"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(ConfigFileNotFound) as excinfo:
        cli.main()
    assert "Cannot found the config file" in str(excinfo.value)


def test_cz_with_arg_but_without_command(mocker: MockFixture):
    testargs = ["cz", "--name", "cz_jira"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoCommandFoundError) as excinfo:
        cli.main()
    assert "Command is required" in str(excinfo.value)


def test_name(mocker: MockFixture, capsys):
    testargs = ["cz", "-n", "cz_jira", "example"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()
    out, _ = capsys.readouterr()
    assert out.startswith("JRA")


@pytest.mark.usefixtures("tmp_git_project")
def test_name_default_value(mocker: MockFixture, capsys):
    testargs = ["cz", "example"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()
    out, _ = capsys.readouterr()
    assert out.startswith("fix: correct minor typos in code")


def test_ls(mocker: MockFixture, capsys):
    testargs = ["cz", "-n", "cz_jira", "ls"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    out, err = capsys.readouterr()

    assert "cz_conventional_commits" in out
    assert isinstance(out, str)


def test_arg_debug(mocker: MockFixture):
    testargs = ["cz", "--debug", "info"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    excepthook = sys.excepthook
    # `sys.excepthook` is replaced by a `partial` in `cli.main`
    # it's not a normal function
    assert isinstance(excepthook, partial)
    assert excepthook.keywords.get("debug") is True


def test_commitizen_excepthook(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.commitizen_excepthook(NotAGitProjectError, NotAGitProjectError(), "")

    assert excinfo.type == SystemExit
    assert excinfo.value.code == NotAGitProjectError.exit_code


def test_commitizen_debug_excepthook(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.commitizen_excepthook(
            NotAGitProjectError,
            NotAGitProjectError(),
            "",
            debug=True,
        )

    assert excinfo.type == SystemExit
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

    assert excinfo.type == SystemExit
    assert excinfo.value.code == 0


def test_parse_no_raise_single_integer():
    input_str = "1"
    result = cli.parse_no_raise(input_str)
    assert result == [1]


def test_parse_no_raise_integers():
    input_str = "1,2,3"
    result = cli.parse_no_raise(input_str)
    assert result == [1, 2, 3]


def test_parse_no_raise_error_code():
    input_str = "NO_COMMITIZEN_FOUND,NO_COMMITS_FOUND,NO_PATTERN_MAP"
    result = cli.parse_no_raise(input_str)
    assert result == [1, 3, 5]


def test_parse_no_raise_mix_integer_error_code():
    input_str = "NO_COMMITIZEN_FOUND,2,NO_COMMITS_FOUND,4"
    result = cli.parse_no_raise(input_str)
    assert result == [1, 2, 3, 4]


def test_parse_no_raise_mix_invalid_arg_is_skipped():
    input_str = "NO_COMMITIZEN_FOUND,2,nothing,4"
    result = cli.parse_no_raise(input_str)
    assert result == [1, 2, 4]


def test_unknown_args_raises(mocker: MockFixture):
    testargs = ["cz", "c", "-this_arg_is_not_supported"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(InvalidCommandArgumentError) as excinfo:
        cli.main()
    assert "Invalid commitizen arguments were found" in str(excinfo.value)


def test_unknown_args_before_double_dash_raises(mocker: MockFixture):
    testargs = ["cz", "c", "-this_arg_is_not_supported", "--"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(InvalidCommandArgumentError) as excinfo:
        cli.main()
    assert "Invalid commitizen arguments were found before -- separator" in str(
        excinfo.value
    )
