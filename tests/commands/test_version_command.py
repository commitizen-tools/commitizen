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
    config.settings["version"] = "0.0.1"
    commands.Version(
        config,
        {"project": True},
    )()
    captured = capsys.readouterr()
    assert "0.0.1" in captured.out


@pytest.mark.parametrize("project", [True, False])
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


@pytest.mark.parametrize("project", [True, False])
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
    ("version", "expected_version"),
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
    ("version", "expected_version"),
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


@pytest.mark.parametrize("argument", ["major", "minor", "patch"])
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
    ("version", "tag_format", "expected_output"),
    [
        ("1.2.3", "v$version", "v1.2.3\n"),
        ("1.2.3", "$version", "1.2.3\n"),
        ("2.0.0", "release-$version", "release-2.0.0\n"),
        ("0.1.0", "ver$version", "ver0.1.0\n"),
    ],
)
def test_version_with_tag_format(
    config, capsys, version: str, tag_format: str, expected_output: str
):
    """Test --tag option applies tag_format to version"""
    config.settings["version"] = version
    config.settings["tag_format"] = tag_format
    commands.Version(
        config,
        {
            "project": True,
            "tag": True,
        },
    )()
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_version_tag_without_project_error(config, capsys):
    """Test --tag requires --project or --verbose"""
    commands.Version(
        config,
        {
            "tag": True,
        },
    )()
    captured = capsys.readouterr()
    assert not captured.out
    assert "Tag can only be used with --project or --verbose." in captured.err


@pytest.mark.parametrize(
    ("next_increment", "current_version", "expected_version"),
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
def test_next_version(
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


@pytest.mark.parametrize(
    ("version", "expected_version"),
    [
        ("1.0.0", "0\n"),
        ("2.1.3", "3\n"),
        ("0.0.1", "1\n"),
        ("0.1.0", "0\n"),
    ],
)
def test_version_just_patch(config, capsys, version: str, expected_version: str):
    config.settings["version"] = version
    commands.Version(
        config,
        {
            "project": True,
            "patch": True,
        },
    )()
    captured = capsys.readouterr()
    assert expected_version == captured.out


def test_version_unknown_scheme(config, capsys):
    config.settings["version"] = "1.0.0"
    config.settings["version_scheme"] = "not_a_registered_scheme_name_xyz"
    commands.Version(config, {"project": True})()
    captured = capsys.readouterr()
    assert "Unknown version scheme." in captured.err


def test_version_use_git_commits_not_implemented(config, capsys):
    config.settings["version"] = "1.0.0"
    commands.Version(
        config,
        {"project": True, "next": "USE_GIT_COMMITS"},
    )()
    captured = capsys.readouterr()
    assert "USE_GIT_COMMITS is not implemented" in captured.err


def test_version_no_arguments_shows_commitizen_version(config, capsys):
    commands.Version(config, {})()
    captured = capsys.readouterr()
    assert captured.out.strip() == __version__
