import platform
import sys

from commitizen import commands
from commitizen.__version__ import __version__


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
        f"Installed Commitizen Version: {__version__}\n" f"Project Version: v0.0.1"
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
