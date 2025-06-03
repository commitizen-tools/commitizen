import platform
import sys

import pytest
from pytest_mock import MockerFixture

from commitizen import cli, commands
from commitizen.__version__ import __version__
from commitizen.config.base_config import BaseConfig
from tests.utils import skip_below_py_3_10


def test_version_for_showing_project_version(config, capsys):
    # No version exist
    commands.Version(
        config,
        {"report": False, "project": True, "commitizen": False, "verbose": False},
    )()
    captured = capsys.readouterr()
    assert "No project information in this project." in captured.err

    config.settings["version"] = "v0.0.1"
    commands.Version(
        config,
        {"report": False, "project": True, "commitizen": False, "verbose": False},
    )()
    captured = capsys.readouterr()
    assert "v0.0.1" in captured.out


def test_version_for_showing_commitizen_version(config, capsys):
    commands.Version(
        config,
        {"report": False, "project": False, "commitizen": True, "verbose": False},
    )()
    captured = capsys.readouterr()
    assert f"{__version__}" in captured.out

    # default showing commitizen version
    commands.Version(
        config,
        {"report": False, "project": False, "commitizen": False, "verbose": False},
    )()
    captured = capsys.readouterr()
    assert f"{__version__}" in captured.out


def test_version_for_showing_both_versions(config, capsys):
    commands.Version(
        config,
        {"report": False, "project": False, "commitizen": False, "verbose": True},
    )()
    captured = capsys.readouterr()
    assert f"Installed Commitizen Version: {__version__}" in captured.out
    assert "No project information in this project." in captured.err

    config.settings["version"] = "v0.0.1"
    commands.Version(
        config,
        {"report": False, "project": False, "commitizen": False, "verbose": True},
    )()
    captured = capsys.readouterr()
    expected_out = (
        f"Installed Commitizen Version: {__version__}\nProject Version: v0.0.1"
    )
    assert expected_out in captured.out


def test_version_for_showing_commitizen_system_info(config, capsys):
    commands.Version(
        config,
        {"report": True, "project": False, "commitizen": False, "verbose": False},
    )()
    captured = capsys.readouterr()
    assert f"Commitizen Version: {__version__}" in captured.out
    assert f"Python Version: {sys.version}" in captured.out
    assert f"Operating System: {platform.system()}" in captured.out


@pytest.mark.parametrize("project", (True, False))
@pytest.mark.usefixtures("tmp_git_project")
def test_version_use_version_provider(
    mocker: MockerFixture,
    config: BaseConfig,
    capsys: pytest.CaptureFixture,
    project: bool,
):
    version = "0.0.0"
    mock = mocker.MagicMock(name="provider")
    mock.get_version.return_value = version
    get_provider = mocker.patch(
        "commitizen.commands.version.get_provider", return_value=mock
    )

    commands.Version(
        config,
        {
            "report": False,
            "project": project,
            "verbose": not project,
        },
    )()
    captured = capsys.readouterr()

    assert version in captured.out
    get_provider.assert_called_once()
    mock.get_version.assert_called_once()
    mock.set_version.assert_not_called()


@skip_below_py_3_10
def test_version_command_shows_description_when_use_help_option(
    mocker: MockerFixture, capsys, file_regression
):
    testargs = ["cz", "version", "--help"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".txt")
