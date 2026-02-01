import platform
import sys

import pytest
from pytest_mock import MockerFixture

from commitizen import commands
from commitizen.__version__ import __version__
from commitizen.config.base_config import BaseConfig


def test_version_for_showing_project_version_error(default_config: BaseConfig, capsys):
    # No version specified in default_config
    commands.Version(
        default_config,
        {"project": True},
    )()
    captured = capsys.readouterr()
    assert "No project information in this project." in captured.err


def test_version_for_showing_project_version(default_config: BaseConfig, capsys):
    default_config.settings["version"] = "v0.0.1"
    commands.Version(
        default_config,
        {"project": True},
    )()
    captured = capsys.readouterr()
    assert "v0.0.1" in captured.out


@pytest.mark.parametrize("project", (True, False))
def test_version_for_showing_commitizen_version(
    default_config: BaseConfig, capsys, project: bool
):
    commands.Version(
        default_config,
        {"project": project, "commitizen": True},
    )()
    captured = capsys.readouterr()
    assert f"{__version__}" in captured.out


def test_version_for_showing_both_versions_no_project(
    default_config: BaseConfig, capsys
):
    commands.Version(
        default_config,
        {"verbose": True},
    )()
    captured = capsys.readouterr()
    assert f"Installed Commitizen Version: {__version__}" in captured.out
    assert "No project information in this project." in captured.err


def test_version_for_showing_both_versions(default_config: BaseConfig, capsys):
    default_config.settings["version"] = "v0.0.1"
    commands.Version(
        default_config,
        {"verbose": True},
    )()
    captured = capsys.readouterr()
    expected_out = (
        f"Installed Commitizen Version: {__version__}\nProject Version: v0.0.1"
    )
    assert expected_out in captured.out


def test_version_for_showing_commitizen_system_info(default_config: BaseConfig, capsys):
    commands.Version(
        default_config,
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
    default_config: BaseConfig,
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
        default_config,
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
def test_version_just_major(
    default_config: BaseConfig, capsys, version: str, expected_version: str
):
    default_config.settings["version"] = version
    commands.Version(
        default_config,
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
def test_version_just_minor(
    default_config: BaseConfig, capsys, version: str, expected_version: str
):
    default_config.settings["version"] = version
    commands.Version(
        default_config,
        {
            "project": True,
            "minor": True,
        },
    )()
    captured = capsys.readouterr()
    assert expected_version == captured.out


@pytest.mark.parametrize("argument", ("major", "minor"))
def test_version_just_major_error_no_project(
    default_config: BaseConfig, capsys, argument: str
):
    commands.Version(
        default_config,
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


@pytest.mark.parametrize(
    "version, tag_format, expected_output",
    [
        ("1.2.3", "v$version", "v1.2.3\n"),
        ("1.2.3", "$version", "1.2.3\n"),
        ("2.0.0", "release-$version", "release-2.0.0\n"),
        ("0.1.0", "ver$version", "ver0.1.0\n"),
    ],
)
def test_version_with_tag_format(
    default_config, capsys, version: str, tag_format: str, expected_output: str
):
    """Test --tag option applies tag_format to version"""
    default_config.settings["version"] = version
    default_config.settings["tag_format"] = tag_format
    commands.Version(
        default_config,
        {
            "project": True,
            "tag": True,
        },
    )()
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_version_tag_without_project_error(default_config: BaseConfig, capsys):
    """Test --tag requires --project or --verbose"""
    commands.Version(
        default_config,
        {
            "tag": True,
        },
    )()
    captured = capsys.readouterr()
    assert not captured.out
    assert "Tag can only be used with --project or --verbose." in captured.err
