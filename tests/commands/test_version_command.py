import platform
import sys

import pytest
from pytest_mock import MockerFixture

from commitizen import commands
from commitizen.__version__ import __version__
from commitizen.config.base_config import BaseConfig
from commitizen.cz.base import BaseCommitizen
from commitizen.exceptions import NoCommitsFoundError, NoPatternMapError
from tests.utils import UtilFixture


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


@pytest.mark.parametrize(
    ("args", "expected_error"),
    [
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
        ({"tag": True}, "Tag can only be used with --project or --verbose."),
    ],
)
def test_version_invalid_combinations(config, capsys, args: dict, expected_error: str):
    """Test that certain flag combinations produce errors."""
    commands.Version(config, args)()  # type: ignore[arg-type]
    captured = capsys.readouterr()
    assert not captured.out
    assert expected_error in captured.err


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


@pytest.mark.parametrize(
    ("commit_message", "expected_version"),
    [
        ("feat: new feature", "1.1.0"),
        ("fix: a bug", "1.0.1"),
        ("feat!: breaking change", "2.0.0"),
        ("docs: update readme", "1.0.0"),
    ],
)
@pytest.mark.usefixtures("tmp_git_project")
def test_version_next_use_git_commits(
    config: BaseConfig,
    capsys: pytest.CaptureFixture,
    util: UtilFixture,
    commit_message: str,
    expected_version: str,
):
    """USE_GIT_COMMITS derives the next version from commits since the last tag."""
    config.settings["version"] = "1.0.0"
    util.create_file_and_commit("feat: initial commit")
    util.create_tag("1.0.0")
    util.create_file_and_commit(commit_message)

    commands.Version(
        config,
        {"project": True, "next": "USE_GIT_COMMITS"},
    )()

    captured = capsys.readouterr()
    assert captured.out == f"{expected_version}\n"


@pytest.mark.usefixtures("tmp_git_project")
def test_version_next_use_git_commits_manual_version(
    config: BaseConfig, capsys: pytest.CaptureFixture, util: UtilFixture
):
    """USE_GIT_COMMITS also works with an explicit MANUAL_VERSION."""
    util.create_file_and_commit("feat: initial commit")
    util.create_tag("1.0.0")
    util.create_file_and_commit("feat: new feature")

    commands.Version(
        config,
        {"manual_version": "1.0.0", "next": "USE_GIT_COMMITS"},
    )()

    captured = capsys.readouterr()
    assert captured.out == "1.1.0\n"


@pytest.mark.usefixtures("tmp_git_project")
def test_version_next_use_git_commits_without_matching_tag(
    config: BaseConfig, capsys: pytest.CaptureFixture, util: UtilFixture
):
    """When no tag matches the current version, all commits are considered."""
    config.settings["version"] = "2.0.0"
    util.create_file_and_commit("feat: initial commit")
    util.create_file_and_commit("feat: new feature")

    commands.Version(
        config,
        {"project": True, "next": "USE_GIT_COMMITS"},
    )()

    captured = capsys.readouterr()
    assert captured.out == "2.1.0\n"


@pytest.mark.usefixtures("tmp_git_project")
def test_version_next_use_git_commits_major_version_zero(
    config: BaseConfig, capsys: pytest.CaptureFixture, util: UtilFixture
):
    """major_version_zero uses the zero bump map so no major bump is emitted."""
    config.settings["version"] = "0.1.0"
    config.settings["major_version_zero"] = True
    util.create_file_and_commit("feat: initial commit")
    util.create_tag("0.1.0")
    util.create_file_and_commit("feat!: breaking change")

    commands.Version(
        config,
        {"project": True, "next": "USE_GIT_COMMITS"},
    )()

    captured = capsys.readouterr()
    assert captured.out == "0.2.0\n"


@pytest.mark.usefixtures("tmp_git_project")
def test_version_next_use_git_commits_prerelease_without_commits(
    config: BaseConfig, capsys: pytest.CaptureFixture, util: UtilFixture
):
    """A prerelease with no new commits finalizes into its release version."""
    config.settings["version"] = "1.0.0rc1"
    util.create_file_and_commit("feat: initial commit")
    util.create_tag("1.0.0rc1")

    commands.Version(
        config,
        {"project": True, "next": "USE_GIT_COMMITS"},
    )()

    captured = capsys.readouterr()
    assert captured.out == "1.0.0\n"


@pytest.mark.usefixtures("tmp_git_project")
def test_version_next_use_git_commits_no_commits_raises(
    config: BaseConfig, util: UtilFixture
):
    """No new commits since the last (non-prerelease) tag raises an error."""
    config.settings["version"] = "1.0.0"
    util.create_file_and_commit("feat: initial commit")
    util.create_tag("1.0.0")

    with pytest.raises(NoCommitsFoundError):
        commands.Version(
            config,
            {"project": True, "next": "USE_GIT_COMMITS"},
        )()


class _NoBumpRulesCz(BaseCommitizen):
    """A commitizen rule without bump pattern or map to trigger NoPatternMapError."""

    bump_pattern = None
    bump_map = None

    def questions(self):
        return []

    def message(self, answers):
        return ""

    def example(self) -> str:
        return ""

    def schema(self) -> str:
        return ""

    def schema_pattern(self) -> str:
        return ""

    def info(self) -> str:
        return ""


@pytest.mark.usefixtures("tmp_git_project")
def test_version_next_use_git_commits_no_pattern_map_raises(
    config: BaseConfig, util: UtilFixture, mocker: MockerFixture
):
    """A rule that does not support bumping raises NoPatternMapError."""
    config.settings["version"] = "1.0.0"
    mocker.patch(
        "commitizen.factory.committer_factory",
        return_value=_NoBumpRulesCz(config),
    )
    util.create_file_and_commit("feat: initial commit")
    util.create_tag("1.0.0")
    util.create_file_and_commit("feat: new feature")

    with pytest.raises(NoPatternMapError):
        commands.Version(
            config,
            {"project": True, "next": "USE_GIT_COMMITS"},
        )()


def test_version_no_arguments_shows_commitizen_version(config, capsys):
    commands.Version(config, {})()
    captured = capsys.readouterr()
    assert captured.out.strip() == __version__
