import platform
import sys

import pytest
from pytest_mock import MockerFixture

from commitizen import commands
from commitizen.__version__ import __version__
from commitizen.config.base_config import BaseConfig


def test_version_for_showing_project_version_error(config, capsys):
    # No version specified in config
    commands.Version(
        config,
        {"project": True},
    )()
    captured = capsys.readouterr()
    assert "No project information in this project." in captured.err


def test_version_for_showing_project_version(config, capsys):
    config.settings["version"] = "v0.0.1"
    commands.Version(
        config,
        {"project": True},
    )()
    captured = capsys.readouterr()
    assert "v0.0.1" in captured.out


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
    config.settings["version"] = "v0.0.1"
    commands.Version(
        config,
        {"verbose": True},
    )()
    captured = capsys.readouterr()
    expected_out = (
        f"Installed Commitizen Version: {__version__}\nProject Version: v0.0.1"
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


@pytest.mark.parametrize("argument", ("major", "minor"))
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
        "Major or minor version can only be used with --project or --verbose."
        in captured.err
    )
