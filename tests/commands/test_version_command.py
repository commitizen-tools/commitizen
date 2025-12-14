import os
import platform
import sys

import pytest
from pytest_mock import MockerFixture

from commitizen import cli, commands
from commitizen.__version__ import __version__
from commitizen.config.base_config import BaseConfig
from tests.utils import skip_below_py_3_10


def test_version_for_showing_project_version_error(config, capsys):
    # No version specified in config
    commands.Version(
        config,
        {"project": True},
    )()
    captured = capsys.readouterr()
    assert "No project information in this project." in captured.err


def test_version_for_showing_project_version(config, capsys):
    config.settings["version"] = "0.0.1"
    commands.Version(
        config,
        {"project": True},
    )()
    captured = capsys.readouterr()
    assert "0.0.1" in captured.out


@pytest.mark.parametrize("project", (True, False))
def test_version_for_showing_commitizen_version(config, capsys, project: bool):
    commands.Version(
        config,
        {"project": project, "commitizen": True},
    )()
    captured = capsys.readouterr()
    assert f"{__version__}" in captured.out


def test_version_for_showing_both_versions_no_project(config, capsys):
    commands.Version(
        config,
        {"verbose": True},
    )()
    captured = capsys.readouterr()
    assert f"Installed Commitizen Version: {__version__}" in captured.out
    assert "No project information in this project." in captured.err


def test_version_for_showing_both_versions(config, capsys):
    config.settings["version"] = "0.0.1"
    commands.Version(
        config,
        {"verbose": True},
    )()
    captured = capsys.readouterr()
    expected_out = (
        f"Installed Commitizen Version: {__version__}\nProject Version: 0.0.1"
    )
    assert expected_out in captured.out


def test_version_for_showing_commitizen_system_info(config, capsys):
    commands.Version(
        config,
        {"report": True},
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
    # Force consistent terminal width for tests to avoid wrapping differences
    # between single and multi-worker pytest modes
    original_columns = os.environ.get("COLUMNS")
    os.environ["COLUMNS"] = "80"

    try:
        testargs = ["cz", "version", "--help"]
        mocker.patch.object(sys, "argv", testargs)
        with pytest.raises(SystemExit):
            cli.main()

        out, _ = capsys.readouterr()
        file_regression.check(out, extension=".txt")
    finally:
        # Restore original COLUMNS
        if original_columns is not None:
            os.environ["COLUMNS"] = original_columns
        else:
            os.environ.pop("COLUMNS", None)


@pytest.mark.parametrize(
    "version, expected_version",
    [
        ("1.0.0", "1\n"),
        ("2.1.3", "2\n"),
        ("0.0.1", "0\n"),
        ("0.1.0", "0\n"),
    ],
)
def test_version_just_major(config, capsys, version: str, expected_version: str):
    config.settings["version"] = version
    commands.Version(
        config,
        {
            "project": True,
            "major": True,
        },
    )()
    captured = capsys.readouterr()
    assert expected_version == captured.out


@pytest.mark.parametrize(
    "version, expected_version",
    [
        ("1.0.0", "0\n"),
        ("2.1.3", "1\n"),
        ("0.0.1", "0\n"),
        ("0.1.0", "1\n"),
    ],
)
def test_version_just_minor(config, capsys, version: str, expected_version: str):
    config.settings["version"] = version
    commands.Version(
        config,
        {
            "project": True,
            "minor": True,
        },
    )()
    captured = capsys.readouterr()
    assert expected_version == captured.out


@pytest.mark.parametrize("argument", ("major", "minor", "patch"))
def test_version_just_major_error_no_project(config, capsys, argument: str):
    commands.Version(
        config,
        {
            argument: True,  # type: ignore[misc]
        },
    )()
    captured = capsys.readouterr()
    assert not captured.out
    assert (
        "can only be used with MANUAL_VERSION, --project or --verbose." in captured.err
    )


@pytest.mark.parametrize(
    "next_increment, current_version, expected_version",
    [
        ("MAJOR", "1.1.0", "2.0.0"),
        ("MAJOR", "1.0.0", "2.0.0"),
        ("MAJOR", "0.0.1", "1.0.0"),
        ("MINOR", "1.1.0", "1.2.0"),
        ("MINOR", "1.0.0", "1.1.0"),
        ("MINOR", "0.0.1", "0.1.0"),
        ("PATCH", "1.1.0", "1.1.1"),
        ("PATCH", "1.0.0", "1.0.1"),
        ("PATCH", "0.0.1", "0.0.2"),
        ("NONE", "1.0.0", "1.0.0"),
    ],
)
def test_next_version_major(
    config, capsys, next_increment: str, current_version: str, expected_version: str
):
    config.settings["version"] = current_version
    for project in (True, False):
        commands.Version(
            config,
            {
                "next": next_increment,
                "project": project,
            },
        )()
        captured = capsys.readouterr()
        assert expected_version in captured.out

    # Use the same settings to test the manual version
    commands.Version(
        config,
        {
            "manual_version": current_version,
            "next": next_increment,
        },
    )()
    captured = capsys.readouterr()
    assert expected_version in captured.out


def test_next_version_invalid_version(config, capsys):
    commands.Version(
        config,
        {
            "manual_version": "INVALID",
        },
    )()
    captured = capsys.readouterr()
    assert "Invalid version: 'INVALID'" in captured.err
