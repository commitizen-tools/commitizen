import sys

from unittest.mock import patch
from pytest_mock import MockFixture

from commitizen import cli
from commitizen.commands.commit import Commit


def test_extra_args_no_raise(mocker: MockFixture):
    testargs = ["cz", "c", "--dry-run", "--", "-extra-args1", "-extra-arg2"]
    extra_cli_args = "-extra-args1 -extra-args2"
    mocker.patch.object(sys, "argv", testargs)
    commit_call = mocker.patch.object(Commit, "__call__")

    def assert_extra_args(self):
        assert self.arguments["extra_cli_args"] == extra_cli_args

    with patch.object(Commit, "test_extra_args", assert_extra_args, autospec=True) as mock:
        commit_call.side_effect = Commit.test_extra_args
        cli.main()
        Commit.__call__.assert_called_once()
