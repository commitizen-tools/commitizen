import subprocess
import sys

import pytest

from commitizen import cli
from commitizen.exceptions import ExpectedExit, NoCommandFoundError, NotAGitProjectError


def test_sysexit_no_argv(mocker, capsys):
    testargs = ["cz"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(ExpectedExit):
        cli.main()
        out, _ = capsys.readouterr()
        assert out.startswith("usage")


def test_cz_with_arg_but_without_command(mocker):
    testargs = ["cz", "--name", "cz_jira"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoCommandFoundError) as excinfo:
        cli.main()
    assert "Command is required" in str(excinfo.value)


def test_name(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "example"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()
    out, _ = capsys.readouterr()
    assert out.startswith("JRA")


@pytest.mark.usefixtures("tmp_git_project")
def test_name_default_value(mocker, capsys):
    testargs = ["cz", "example"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()
    out, _ = capsys.readouterr()
    assert out.startswith("fix: correct minor typos in code")


def test_ls(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "ls"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    out, err = capsys.readouterr()

    assert "cz_conventional_commits" in out
    assert isinstance(out, str)


def test_arg_debug(mocker):
    testargs = ["cz", "--debug", "info"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    assert sys.excepthook.keywords.get("debug") is True


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


def test_argcomplete_activation():
    """
    This function is testing the one-time activation of argcomplete for
    commitizen only.

    Equivalent to run:
    $ eval "$(register-python-argcomplete pytest)"
    """
    output = subprocess.run(["register-python-argcomplete", "cz"])

    assert output.returncode == 0
