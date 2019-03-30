import sys
import pytest
from commitizen import cli


def test_sysexit_no_argv():
    with pytest.raises(SystemExit):
        cli.main()


def test_ls(mocker, capsys):
    testargs = ["cz", "-n", "cz_jira", "ls"]
    mocker.patch.object(sys, 'argv', testargs)
    cli.main()
    out, err = capsys.readouterr()

    assert "cz_conventional_commits" in out
    assert isinstance(out, str)


def test_version(mocker):
    testargs = ["cz", "--version"]
    with pytest.raises(SystemExit):
        mocker.patch.object(sys, 'argv', testargs)
        cli.main()