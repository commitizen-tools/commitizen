import os
from unittest.mock import call

import pytest
from pytest_mock import MockFixture

from commitizen import cmd, hooks
from commitizen.exceptions import RunHookError


def test_run(mocker: MockFixture):
    bump_hooks = ["pre_bump_hook", "pre_bump_hook_1"]

    cmd_run_mock = mocker.Mock()
    cmd_run_mock.return_value.return_code = 0
    mocker.patch.object(cmd, "run", cmd_run_mock)

    hooks.run(bump_hooks)

    cmd_run_mock.assert_has_calls(
        [
            call("pre_bump_hook", env=dict(os.environ)),
            call("pre_bump_hook_1", env=dict(os.environ)),
        ]
    )


def test_run_error(mocker: MockFixture):
    bump_hooks = ["pre_bump_hook", "pre_bump_hook_1"]

    cmd_run_mock = mocker.Mock()
    cmd_run_mock.return_value.return_code = 1
    mocker.patch.object(cmd, "run", cmd_run_mock)

    with pytest.raises(RunHookError):
        hooks.run(bump_hooks)


def test_format_env():
    result = hooks._format_env("TEST_", {"foo": "bar", "bar": "baz"})
    assert "TEST_FOO" in result and result["TEST_FOO"] == "bar"
    assert "TEST_BAR" in result and result["TEST_BAR"] == "baz"
