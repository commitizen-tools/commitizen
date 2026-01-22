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


@pytest.mark.parametrize(
    "args, expected_error",
    [
        # --next without version source
        ({"next": "MAJOR"}, "No project information in this project."),
        ({"next": "MINOR"}, "No project information in this project."),
        ({"next": "PATCH"}, "No project information in this project."),
        # --major/--minor/--patch without project/verbose/manual_version
        (
            {"major": True},
            "can only be used with MANUAL_VERSION, --project or --verbose.",
        ),
        (
            {"minor": True},
            "can only be used with MANUAL_VERSION, --project or --verbose.",
        ),
        (
            {"patch": True},
            "can only be used with MANUAL_VERSION, --project or --verbose.",
        ),
        # Invalid version
        ({"manual_version": "INVALID"}, "Invalid version: 'INVALID'"),
        ({"manual_version": "not.a.version"}, "Invalid version: 'not.a.version'"),
        # Invalid version with --next
        ({"manual_version": "INVALID", "next": "MAJOR"}, "Invalid version: 'INVALID'"),
        ({"manual_version": "INVALID", "next": "MINOR"}, "Invalid version: 'INVALID'"),
        ({"manual_version": "INVALID", "next": "PATCH"}, "Invalid version: 'INVALID'"),
        # Invalid version with --major/--minor/--patch
        ({"manual_version": "INVALID", "major": True}, "Invalid version: 'INVALID'"),
        ({"manual_version": "INVALID", "minor": True}, "Invalid version: 'INVALID'"),
        ({"manual_version": "INVALID", "patch": True}, "Invalid version: 'INVALID'"),
    ],
)
def test_version_invalid_combinations(config, capsys, args: dict, expected_error: str):
    """Test all invalid argument combinations."""
    commands.Version(config, args)()  # type: ignore[arg-type]
    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_next_with_use_git_commits(config, capsys):
    """Test that --next USE_GIT_COMMITS raises NotImplementedError."""
    config.settings["version"] = "1.0.0"
    with pytest.raises(NotImplementedError, match="USE_GIT_COMMITS is not implemented"):
        commands.Version(
            config,
            {
                "next": "USE_GIT_COMMITS",
                "project": True,
            },
        )()


@pytest.mark.parametrize(
    "next_increment, component, expected_output",
    [
        ("MAJOR", "major", "2\n"),  # 1.0.0 -> 2.0.0, major is 2
        ("MINOR", "minor", "1\n"),  # 1.0.0 -> 1.1.0, minor is 1
        ("PATCH", "patch", "1\n"),  # 1.0.0 -> 1.0.1, patch is 1
    ],
)
def test_next_with_component_combination(
    config, capsys, next_increment: str, component: str, expected_output: str
):
    """Test that --next combined with --major/--minor/--patch works (next is processed first)."""
    config.settings["version"] = "1.0.0"
    commands.Version(
        config,
        {
            "next": next_increment,
            component: True,  # type: ignore[misc]
            "project": True,
        },
    )()
    captured = capsys.readouterr()
    assert expected_output == captured.out


@pytest.mark.parametrize(
    "invalid_increment",
    ["INVALID_INCREMENT", "invalid", "PATCH_MINOR", ""],
)
def test_next_with_invalid_increment_value(config, capsys, invalid_increment: str):
    """Test that --next with invalid increment value uses NONE (no error, but no bump)."""
    config.settings["version"] = "1.0.0"
    commands.Version(
        config,
        {
            "next": invalid_increment,
            "project": True,
        },
    )()
    captured = capsys.readouterr()
    # VersionIncrement.from_value returns NONE for invalid values, so version stays 1.0.0
    assert "1.0.0" in captured.out
