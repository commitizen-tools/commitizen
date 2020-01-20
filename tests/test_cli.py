import sys

import pytest

from commitizen import cli
from commitizen.__version__ import __version__


def test_sysexit_no_argv(mocker, capsys):
    testargs = ["cz"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(SystemExit):
        cli.main()
        out, _ = capsys.readouterr()
        assert out.startswith("usage")


def test_cz_with_arg_but_without_command(mocker, capsys):
    testargs = ["cz", "--name", "cz_jira"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(SystemExit):
        cli.main()
        _, err = capsys.readouterr()
        assert "Command is required" in err


def test_name(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "example"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()
    out, _ = capsys.readouterr()
    assert out.startswith("JRA")


def test_name_default_value(tmpdir, mocker, capsys):
    with tmpdir.as_cwd() as _:
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


def test_version(mocker, capsys):
    testargs = ["cz", "--version"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()
    out, _ = capsys.readouterr()
    assert out.strip() == __version__
