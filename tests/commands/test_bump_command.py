from __future__ import annotations

import inspect
import re
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest.mock import call

import pytest

import commitizen.commands.bump as bump
from commitizen import cmd, defaults, git, hooks
from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import (
    BumpTagFailedError,
    CommitizenException,
    CurrentVersionNotFoundError,
    DryRunExit,
    ExitCode,
    ExpectedExit,
    InvalidManualVersion,
    NoCommitsFoundError,
    NoneIncrementExit,
    NoPatternMapError,
    NotAGitProjectError,
    NotAllowed,
    NoVersionSpecifiedError,
)

if TYPE_CHECKING:
    import py
    from pytest_mock import MockFixture
    from pytest_regressions.file_regression import FileRegressionFixture

    from commitizen.changelog_formats import ChangelogFormat
    from commitizen.cz.base import BaseCommitizen
    from tests.utils import UtilFixture


@pytest.mark.parametrize(
    "commit_msg",
    [
        "fix: username exception",
        "fix(user): username exception",
        "refactor: remove ini configuration support",
        "refactor(config): remove ini configuration support",
        "perf: update to use multiprocess",
        "perf(worker): update to use multiprocess",
    ],
)
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_patch_increment(commit_msg: str, util: UtilFixture):
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.1.1") is True


@pytest.mark.parametrize("commit_msg", ["feat: new file", "feat(user): new file"])
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_minor_increment(commit_msg: str, util: UtilFixture):
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True
    assert (
        "commit:refs/tags/0.2.0"
        in cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"').out
    )


@pytest.mark.parametrize("commit_msg", ["feat: new file", "feat(user): new file"])
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_minor_increment_annotated(commit_msg: str, util: UtilFixture):
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes", "--annotated-tag")
    assert git.tag_exist("0.2.0") is True
    assert (
        "tag:refs/tags/0.2.0"
        in cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"').out
    )

    assert git.is_signed_tag("0.2.0") is False


@pytest.mark.parametrize("commit_msg", ["feat: new file", "feat(user): new file"])
@pytest.mark.usefixtures("tmp_commitizen_project_with_gpg")
def test_bump_minor_increment_signed(commit_msg: str, util: UtilFixture):
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes", "--gpg-sign")
    assert git.tag_exist("0.2.0") is True
    assert (
        "tag:refs/tags/0.2.0"
        in cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"').out
    )

    assert git.is_signed_tag("0.2.0") is True


@pytest.mark.parametrize("commit_msg", ["feat: new file", "feat(user): new file"])
def test_bump_minor_increment_annotated_config_file(
    commit_msg: str, util: UtilFixture, pyproject: Path
):
    with pyproject.open("a", encoding="utf-8") as f:
        f.write("\nannotated_tag = 1")
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True
    assert (
        "tag:refs/tags/0.2.0"
        in cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"').out
    )

    assert git.is_signed_tag("0.2.0") is False


@pytest.mark.parametrize("commit_msg", ["feat: new file", "feat(user): new file"])
def test_bump_minor_increment_signed_config_file(
    commit_msg: str, util: UtilFixture, tmp_commitizen_project_with_gpg
):
    tmp_commitizen_cfg_file = tmp_commitizen_project_with_gpg.join("pyproject.toml")
    with Path(tmp_commitizen_cfg_file).open("a", encoding="utf-8") as f:
        f.write("\ngpg_sign = 1")
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True
    assert (
        "tag:refs/tags/0.2.0"
        in cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"').out
    )

    assert git.is_signed_tag("0.2.0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "commit_msg",
    [
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface",
        "feat(user): new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface",
        "BREAKING CHANGE: age is no longer supported",
        "BREAKING-CHANGE: age is no longer supported",
    ],
)
def test_bump_major_increment(commit_msg: str, util: UtilFixture):
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes")
    assert git.tag_exist("1.0.0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "commit_msg",
    [
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface",
        "feat(user): new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface",
        "BREAKING CHANGE: age is no longer supported",
        "BREAKING-CHANGE: age is no longer supported",
    ],
)
def test_bump_major_increment_major_version_zero(commit_msg: str, util: UtilFixture):
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes", "--major-version-zero")
    assert git.tag_exist("0.2.0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    ("commit_msg", "increment", "expected_tag"),
    [
        ("feat: new file", "PATCH", "0.1.1"),
        ("fix: username exception", "major", "1.0.0"),
        ("refactor: remove ini configuration support", "patch", "0.1.1"),
        ("BREAKING CHANGE: age is no longer supported", "minor", "0.2.0"),
    ],
)
def test_bump_command_increment_option(
    commit_msg: str, increment: str, expected_tag: str, util: UtilFixture
):
    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--increment", increment, "--yes")
    assert git.tag_exist(expected_tag) is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_prerelease(util: UtilFixture):
    util.create_file_and_commit("feat: location")

    # Create an alpha pre-release.
    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.2.0a0") is True

    # Create a beta pre-release.
    util.run_cli("bump", "--prerelease", "beta", "--yes")
    assert git.tag_exist("0.2.0b0") is True

    # With a current beta pre-release, bumping alpha must bump beta
    # because we can't bump "backwards".
    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.2.0a1") is False
    assert git.tag_exist("0.2.0b1") is True

    # Create a rc pre-release.
    util.run_cli("bump", "--prerelease", "rc", "--yes")
    assert git.tag_exist("0.2.0rc0") is True

    # With a current rc pre-release, bumping alpha must bump rc.
    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.2.0a1") is False
    assert git.tag_exist("0.2.0b2") is False
    assert git.tag_exist("0.2.0rc1") is True

    # With a current rc pre-release, bumping beta must bump rc.
    util.run_cli("bump", "--prerelease", "beta", "--yes")
    assert git.tag_exist("0.2.0a2") is False
    assert git.tag_exist("0.2.0b2") is False
    assert git.tag_exist("0.2.0rc2") is True

    # Create a final release from the current pre-release.
    util.run_cli("bump")
    assert git.tag_exist("0.2.0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_prerelease_increment(util: UtilFixture):
    # FINAL RELEASE
    util.create_file_and_commit("fix: location")
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.1.1") is True

    # PRERELEASE
    util.create_file_and_commit("fix: location")
    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.1.2a0") is True

    util.create_file_and_commit("feat: location")
    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.2.0a0") is True

    util.create_file_and_commit("feat!: breaking")
    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("1.0.0a0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_prerelease_exact_mode(util: UtilFixture):
    # PRERELEASE
    util.create_file_and_commit("feat: location")
    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.2.0a0") is True

    # PRERELEASE + PATCH BUMP
    util.run_cli("bump", "--prerelease", "alpha", "--yes", "--increment-mode=exact")
    assert git.tag_exist("0.2.0a1") is True

    # PRERELEASE + MINOR BUMP
    # --increment-mode allows the minor version to bump, and restart the prerelease
    util.create_file_and_commit("feat: location")
    util.run_cli("bump", "--prerelease", "alpha", "--yes", "--increment-mode=exact")
    assert git.tag_exist("0.3.0a0") is True

    # PRERELEASE + MAJOR BUMP
    # --increment-mode=exact allows the major version to bump, and restart the prerelease
    util.run_cli(
        "bump",
        "--prerelease",
        "alpha",
        "--yes",
        "--increment=MAJOR",
        "--increment-mode=exact",
    )

    assert git.tag_exist("1.0.0a0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_on_git_with_hooks_no_verify_disabled(util: UtilFixture):
    """Bump commit without --no-verify"""
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/pre-commit", "w", encoding="utf-8") as f:
        f.write('#!/usr/bin/env bash\necho "0.1.0"')
    cmd.run("chmod +x .git/hooks/pre-commit")

    # MINOR
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_tag_exists_raises_exception(util: UtilFixture):
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/post-commit", "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\nexit 9")
    cmd.run("chmod +x .git/hooks/post-commit")

    # MINOR
    util.create_file_and_commit("feat: new file")
    git.tag("0.2.0")

    with pytest.raises(BumpTagFailedError, match=re.escape("0.2.0")):
        util.run_cli("bump", "--yes")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_on_git_with_hooks_no_verify_enabled(util: UtilFixture):
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/pre-commit", "w", encoding="utf-8") as f:
        f.write('#!/usr/bin/env bash\necho "0.1.0"')
    cmd.run("chmod +x .git/hooks/pre-commit")

    # MINOR
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes", "--no-verify")
    assert git.tag_exist("0.2.0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_when_bumping_is_not_support(util: UtilFixture):
    util.create_file_and_commit(
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported"
    )

    with pytest.raises(NoPatternMapError, match="'cz_jira' rule does not support bump"):
        util.run_cli("-n", "cz_jira", "bump", "--yes")


@pytest.mark.usefixtures("tmp_git_project")
def test_bump_when_version_is_not_specify(util: UtilFixture):
    with pytest.raises(
        NoVersionSpecifiedError, match=re.escape(NoVersionSpecifiedError.message)
    ):
        util.run_cli("bump")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_when_no_new_commit(util: UtilFixture):
    """bump without any commits since the last bump."""
    # We need this first commit otherwise the revision is invalid.
    util.create_file_and_commit("feat: initial")

    util.run_cli("bump", "--yes")

    # bump without a new commit.
    with pytest.raises(
        NoCommitsFoundError, match=r"\[NO_COMMITS_FOUND\]\nNo new commits found\."
    ):
        util.run_cli("bump", "--yes")


def test_bump_when_version_inconsistent_in_version_files(
    tmp_commitizen_project, util: UtilFixture
):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("100.999.10000")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
    with Path(tmp_commitizen_cfg_file).open("a", encoding="utf-8") as f:
        f.write(f'\nversion_files = ["{tmp_version_file_string}"]')

    util.create_file_and_commit("feat: new file")

    with pytest.raises(
        CurrentVersionNotFoundError, match="Current version 0.1.0 is not found in"
    ):
        util.run_cli("bump", "--yes", "--check-consistency")


def test_bump_major_version_zero_when_major_is_not_zero(
    tmp_commitizen_project, util: UtilFixture
):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("1.0.0")
    tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write(
        f"[tool.commitizen]\n"
        'version="1.0.0"\n'
        f'version_files = ["{str(tmp_version_file_string)}"]'
    )
    tmp_changelog_file = tmp_commitizen_project.join("CHANGELOG.md")
    tmp_changelog_file.write("## v1.0.0")

    util.create_file_and_commit("feat(user): new file")
    util.create_tag("v1.0.0")
    util.create_file_and_commit("feat(user)!: new file")

    with pytest.raises(
        NotAllowed,
        match="--major-version-zero is meaningless for current version 1.0.0",
    ):
        util.run_cli("bump", "--yes", "--major-version-zero")


def test_bump_files_only(tmp_commitizen_project, util: UtilFixture):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("0.1.0")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
    with Path(tmp_commitizen_cfg_file).open("a", encoding="utf-8") as f:
        f.write(f'\nversion_files = ["{tmp_version_file_string}"]')

    util.create_file_and_commit("feat: new user interface")
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True

    util.create_file_and_commit("feat: another new feature")
    with pytest.raises(ExpectedExit):
        util.run_cli("bump", "--yes", "--version-files-only")

    assert git.tag_exist("0.3.0") is False

    assert "0.3.0" in Path(tmp_version_file).read_text(encoding="utf-8")

    assert "0.3.0" in Path(tmp_commitizen_cfg_file).read_text(encoding="utf-8")


def test_bump_local_version(tmp_commitizen_project, util: UtilFixture):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("4.5.1+0.1.0")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
    tmp_commitizen_cfg_file.write(
        f"[tool.commitizen]\n"
        'version="4.5.1+0.1.0"\n'
        f'version_files = ["{tmp_version_file_string}"]'
    )

    util.create_file_and_commit("feat: new user interface")
    util.run_cli("bump", "--yes", "--local-version")
    assert git.tag_exist("4.5.1+0.2.0") is True

    assert "4.5.1+0.2.0" in Path(tmp_version_file).read_text(encoding="utf-8")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_dry_run(util: UtilFixture, capsys: pytest.CaptureFixture):
    util.create_file_and_commit("feat: new file")

    with pytest.raises(DryRunExit):
        util.run_cli("bump", "--yes", "--dry-run")

    out, _ = capsys.readouterr()
    assert "0.2.0" in out
    assert git.tag_exist("0.2.0") is False


def test_bump_in_non_git_project(tmpdir, util: UtilFixture):
    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            with pytest.raises(ExpectedExit):
                util.run_cli("bump", "--yes")


def test_none_increment_exit_should_be_a_class():
    assert inspect.isclass(NoneIncrementExit)


def test_none_increment_exit_should_be_expected_exit_subclass():
    assert issubclass(NoneIncrementExit, CommitizenException)


def test_none_increment_exit_should_exist_in_bump():
    assert hasattr(bump, "NoneIncrementExit")


def test_none_increment_exit_is_exception():
    assert bump.NoneIncrementExit == NoneIncrementExit


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_none_increment_should_not_call_git_tag_and_error_code_is_not_zero(
    mocker: MockFixture,
    util: UtilFixture,
):
    util.create_file_and_commit("test(test_get_all_droplets): fix bad comparison test")
    git_tag_mock = mocker.patch("commitizen.git.tag")

    with pytest.raises(NoneIncrementExit) as e:
        util.run_cli("bump", "--yes")

    git_tag_mock.assert_not_called()
    assert e.value.exit_code == ExitCode.NO_INCREMENT


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_arg(util: UtilFixture, changelog_path):
    util.create_file_and_commit("feat(user): new file")
    util.run_cli("bump", "--yes", "--changelog")
    assert git.tag_exist("0.2.0") is True

    out = changelog_path.read_text(encoding="utf-8")
    assert out.startswith("#")
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_config(util: UtilFixture, changelog_path, config_path):
    util.create_file_and_commit("feat(user): new file")
    with config_path.open("a", encoding="utf-8") as fp:
        fp.write("update_changelog_on_bump = true\n")

    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True

    out = changelog_path.read_text(encoding="utf-8")
    assert out.startswith("#")
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_prevent_prerelease_when_no_increment_detected(
    util: UtilFixture, capsys: pytest.CaptureFixture
):
    util.create_file_and_commit("feat: new file")

    util.run_cli("bump", "--yes")
    out, _ = capsys.readouterr()

    assert "0.2.0" in out

    util.create_file_and_commit("test: new file")

    with pytest.raises(
        NoCommitsFoundError,
        match=re.escape(
            "[NO_COMMITS_FOUND]\nNo commits found to generate a pre-release."
        ),
    ):
        util.run_cli("bump", "-pr", "beta")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_to_stdout_arg(
    util: UtilFixture, capsys: pytest.CaptureFixture, changelog_path: Path
):
    util.create_file_and_commit("feat(user): this should appear in stdout")
    util.run_cli("bump", "--yes", "--changelog-to-stdout")
    out, _ = capsys.readouterr()

    assert "this should appear in stdout" in out
    assert git.tag_exist("0.2.0") is True

    out = changelog_path.read_text(encoding="utf-8")
    assert out.startswith("#")
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_to_stdout_dry_run_arg(
    util: UtilFixture, capsys: pytest.CaptureFixture, changelog_path: Path
):
    util.create_file_and_commit(
        "feat(user): this should appear in stdout with dry-run enabled"
    )
    with pytest.raises(DryRunExit):
        util.run_cli("bump", "--yes", "--changelog-to-stdout", "--dry-run")
    out, _ = capsys.readouterr()

    assert git.tag_exist("0.2.0") is False
    assert out.startswith("#")
    assert "this should appear in stdout with dry-run enabled" in out
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_without_git_to_stdout_arg(
    util: UtilFixture, capsys: pytest.CaptureFixture
):
    util.create_file_and_commit("feat(user): this should appear in stdout")
    util.run_cli("bump", "--yes")
    out, _ = capsys.readouterr()

    assert (
        re.search(r"^\[master \w+] bump: version 0.1.0 → 0.2.0", out, re.MULTILINE)
        is not None
    )


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_git_to_stdout_arg(util: UtilFixture, capsys: pytest.CaptureFixture):
    util.create_file_and_commit("feat(user): this should appear in stdout")
    util.run_cli("bump", "--yes", "--git-output-to-stderr")
    out, _ = capsys.readouterr()

    assert (
        re.search(r"^\[master \w+] bump: version 0.1.0 → 0.2.0", out, re.MULTILINE)
        is None
    )


@pytest.mark.parametrize(
    ("version_filepath", "version_regex", "version_file_content"),
    [
        pytest.param(
            "pyproject.toml",
            "pyproject.toml:^version",
            """
[tool.poetry]
name = "my_package"
version = "0.1.0"
""",
            id="version in pyproject.toml with regex",
        ),
        pytest.param(
            "pyproject.toml",
            "pyproject.toml",
            """
[tool.poetry]
name = "my_package"
version = "0.1.0"
""",
            id="version in pyproject.toml without regex",
        ),
        pytest.param(
            "__init__.py",
            "__init__.py:^__version__",
            """
'''This is a test file.'''
__version__ = "0.1.0"
""",
            id="version in __init__.py with regex",
        ),
        pytest.param(
            "pyproject.toml",
            "*.toml:^version",
            """
[tool.poetry]
name = "my_package"
version = "0.1.0"
""",
            id="version in pyproject.toml with glob and regex",
        ),
    ],
)
@pytest.mark.parametrize(
    "cli_bump_changelog_args",
    [
        ("bump", "--changelog", "--yes"),
        (
            "bump",
            "--changelog",
            "--changelog-to-stdout",
            "--annotated-tag",
            "--check-consistency",
            "--yes",
        ),
    ],
    ids=lambda cmd_tuple: " ".join(["cz", *cmd_tuple])
    if isinstance(cmd_tuple, tuple)
    else cmd_tuple,
)
def test_bump_changelog_command_commits_untracked_changelog_and_version_files(
    tmp_commitizen_project,
    util: UtilFixture,
    cli_bump_changelog_args: tuple[str, ...],
    version_filepath: str,
    version_regex: str,
    version_file_content: str,
):
    """Ensure that changelog always gets committed, no matter what version file or cli options get passed.

    Steps:
     - Append the version file's name and regex commitizen configuration lines to `pyproject.toml`.
     - Append to or create the version file.
     - Add a commit of type fix to be eligible for a version bump.
     - Call commitizen main cli and assert that the `CHANGELOG.md` and the version file were committed.
    """

    with tmp_commitizen_project.join("pyproject.toml").open(
        mode="a",
        encoding="utf-8",
    ) as commitizen_config:
        commitizen_config.write(f"version_files = [\n'{version_regex}'\n]")

    with tmp_commitizen_project.join(version_filepath).open(
        mode="a+", encoding="utf-8"
    ) as version_file:
        version_file.write(version_file_content)

    util.create_file_and_commit("fix: some test commit")

    util.run_cli(*cli_bump_changelog_args)

    commit_file_names = git.get_filenames_in_commit()
    assert "CHANGELOG.md" in commit_file_names
    assert version_filepath in commit_file_names


@pytest.mark.parametrize(
    "testargs",
    [
        ["--local-version", "1.2.3"],
        ["--prerelease", "rc", "1.2.3"],
        ["--devrelease", "0", "1.2.3"],
        ["--devrelease", "1", "1.2.3"],
        ["--increment", "PATCH", "1.2.3"],
        ["--build-metadata=a.b.c", "1.2.3"],
        ["--local-version", "--build-metadata=a.b.c"],
    ],
)
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_invalid_manual_args_raises_exception(util: UtilFixture, testargs):
    with pytest.raises(NotAllowed):
        util.run_cli("bump", *testargs)


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "manual_version",
    [
        "noversion",
        "1.2..3",
    ],
)
def test_bump_invalid_manual_version_raises_exception(
    util: UtilFixture, manual_version
):
    util.create_file_and_commit("feat: new file")

    with pytest.raises(
        InvalidManualVersion,
        match=re.escape(
            f"[INVALID_MANUAL_VERSION]\nInvalid manual version: '{manual_version}'"
        ),
    ):
        util.run_cli("bump", "--yes", manual_version)


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "manual_version",
    [
        "0.0.1",
        "0.1.0rc2",
        "0.1.0.dev2",
        "0.1.0+1.0.0",
        "0.1.0rc2.dev2+1.0.0",
        "0.1.1",
        "0.2.0",
        "1.0.0",
        "1.2",
        "1",
    ],
)
def test_bump_manual_version(util: UtilFixture, manual_version):
    util.create_file_and_commit("feat: new file")

    util.run_cli("bump", "--yes", manual_version)
    assert git.tag_exist(manual_version) is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_manual_version_disallows_major_version_zero(util: UtilFixture):
    util.create_file_and_commit("feat: new file")
    with pytest.raises(
        NotAllowed,
        match="--major-version-zero cannot be combined with MANUAL_VERSION",
    ):
        util.run_cli("bump", "--yes", "--major-version-zero", "0.2.0")


@pytest.mark.parametrize(
    ("initial_version", "expected_version_after_bump"),
    [
        ("1", "1.1.0"),
        ("1.2", "1.3.0"),
    ],
)
def test_bump_version_with_less_components_in_config(
    tmp_commitizen_project_initial,
    initial_version,
    expected_version_after_bump,
    util: UtilFixture,
):
    tmp_commitizen_project = tmp_commitizen_project_initial(version=initial_version)
    util.run_cli("bump", "--yes")

    assert git.tag_exist(expected_version_after_bump) is True

    for version_file in [
        tmp_commitizen_project.join("__version__.py"),
        tmp_commitizen_project.join("pyproject.toml"),
    ]:
        assert expected_version_after_bump in Path(version_file).read_text(
            encoding="utf-8"
        )


@pytest.mark.parametrize("commit_msg", ["feat: new file", "feat(user): new file"])
def test_bump_with_pre_bump_hooks(
    commit_msg, mocker: MockFixture, tmp_commitizen_project, util: UtilFixture
):
    pre_bump_hook = "scripts/pre_bump_hook.sh"
    post_bump_hook = "scripts/post_bump_hook.sh"

    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    with Path(tmp_commitizen_cfg_file).open("a", encoding="utf-8") as f:
        f.write(
            f'\npre_bump_hooks = ["{pre_bump_hook}"]\n'
            f'post_bump_hooks = ["{post_bump_hook}"]\n'
        )

    run_mock = mocker.Mock()
    mocker.patch.object(hooks, "run", run_mock)

    util.create_file_and_commit(commit_msg)
    util.run_cli("bump", "--yes")

    assert git.tag_exist("0.2.0") is True

    run_mock.assert_has_calls(
        [
            call(
                [pre_bump_hook],
                _env_prefix="CZ_PRE_",
                is_initial=True,
                current_version="0.1.0",
                current_tag_version="0.1.0",
                new_version="0.2.0",
                new_tag_version="0.2.0",
                message="bump: version 0.1.0 → 0.2.0",
                increment="MINOR",
                changelog_file_name=None,
            ),
            call(
                [post_bump_hook],
                _env_prefix="CZ_POST_",
                was_initial=True,
                previous_version="0.1.0",
                previous_tag_version="0.1.0",
                current_version="0.2.0",
                current_tag_version="0.2.0",
                message="bump: version 0.1.0 → 0.2.0",
                increment="MINOR",
                changelog_file_name=None,
            ),
        ]
    )


def test_bump_with_hooks_and_increment(
    mocker: MockFixture, tmp_commitizen_project, util: UtilFixture
):
    pre_bump_hook = "scripts/pre_bump_hook.sh"
    post_bump_hook = "scripts/post_bump_hook.sh"

    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    with Path(tmp_commitizen_cfg_file).open("a", encoding="utf-8") as f:
        f.write(
            f'\npre_bump_hooks = ["{pre_bump_hook}"]\n'
            f'post_bump_hooks = ["{post_bump_hook}"]\n'
        )

    run_mock = mocker.Mock()
    mocker.patch.object(hooks, "run", run_mock)

    util.create_file_and_commit("test: some test")
    util.run_cli("bump", "--yes", "--increment", "MINOR")

    assert git.tag_exist("0.2.0") is True


@pytest.mark.usefixtures("tmp_git_project")
def test_bump_use_version_provider(mocker: MockFixture, util: UtilFixture):
    mock = mocker.MagicMock(name="provider")
    mock.get_version.return_value = "0.0.0"
    get_provider = mocker.patch(
        "commitizen.commands.bump.get_provider", return_value=mock
    )

    util.create_file_and_commit("fix: fake commit")
    util.run_cli("bump", "--yes", "--changelog")

    assert git.tag_exist("0.0.1") is True
    get_provider.assert_called_once()
    mock.get_version.assert_called_once()
    mock.set_version.assert_called_once_with("0.0.1")


def test_bump_command_prerelease_scheme_via_cli(
    tmp_commitizen_project_initial, util: UtilFixture
):
    tmp_commitizen_project = tmp_commitizen_project_initial()
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")

    util.run_cli(
        "bump",
        "--prerelease",
        "alpha",
        "--yes",
        "--version-scheme",
        "semver",
    )
    assert git.tag_exist("0.2.0-a0") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0-a0" in Path(version_file).read_text(encoding="utf-8")

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0" in Path(version_file).read_text(encoding="utf-8")


def test_bump_command_prerelease_scheme_via_config(
    tmp_commitizen_project_initial, util: UtilFixture
):
    tmp_commitizen_project = tmp_commitizen_project_initial(
        config_extra='version_scheme = "semver"\n',
    )
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")

    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.2.0-a0") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0-a0" in Path(version_file).read_text(encoding="utf-8")

    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("0.2.0-a1") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0-a1" in Path(version_file).read_text(encoding="utf-8")

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    util.run_cli("bump", "--yes")
    assert git.tag_exist("0.2.0") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0" in Path(version_file).read_text(encoding="utf-8")


def test_bump_command_prerelease_scheme_check_old_tags(
    tmp_commitizen_project_initial, util: UtilFixture
):
    tmp_commitizen_project = tmp_commitizen_project_initial(
        config_extra=('tag_format = "v$version"\nversion_scheme = "semver"\n'),
    )
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")

    util.run_cli("bump", "--prerelease", "alpha", "--yes")
    assert git.tag_exist("v0.2.0-a0") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0-a0" in Path(version_file).read_text(encoding="utf-8")

    util.run_cli("bump", "--prerelease", "alpha")
    assert git.tag_exist("v0.2.0-a1") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0-a1" in Path(version_file).read_text(encoding="utf-8")

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    util.run_cli("bump")
    assert git.tag_exist("v0.2.0") is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        assert "0.2.0" in Path(version_file).read_text(encoding="utf-8")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.usefixtures("use_cz_semver")
@pytest.mark.parametrize(
    ("message", "expected_tag"),
    [
        ("minor: add users", "0.2.0"),
        ("patch: bug affecting users", "0.1.1"),
        ("major: bug affecting users", "1.0.0"),
    ],
)
def test_bump_with_plugin(util: UtilFixture, message: str, expected_tag: str):
    util.create_file_and_commit(message)
    util.run_cli("--name", "cz_semver", "bump", "--yes")
    assert git.tag_exist(expected_tag) is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.usefixtures("use_cz_semver")
@pytest.mark.parametrize(
    ("message", "expected_tag"),
    [
        ("minor: add users", "0.2.0"),
        ("patch: bug affecting users", "0.1.1"),
        ("major: bug affecting users", "0.2.0"),
    ],
)
def test_bump_with_major_version_zero_with_plugin(
    util: UtilFixture, message: str, expected_tag: str
):
    util.create_file_and_commit(message)
    util.run_cli("--name", "cz_semver", "bump", "--yes", "--major-version-zero")
    assert git.tag_exist(expected_tag) is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_version_type_deprecation(util: UtilFixture):
    util.create_file_and_commit("feat: check deprecation on --version-type")

    with pytest.warns(DeprecationWarning, match=r".*--version-type.*deprecated"):
        util.run_cli(
            "bump",
            "--prerelease",
            "alpha",
            "--yes",
            "--version-type",
            "semver",
        )

    assert git.tag_exist("0.2.0-a0") is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_version_scheme_priority_over_version_type(util: UtilFixture):
    util.create_file_and_commit("feat: check deprecation on --version-type")

    with pytest.warns(DeprecationWarning, match=r".*--version-type.*deprecated"):
        util.run_cli(
            "bump",
            "--prerelease",
            "alpha",
            "--yes",
            "--version-type",
            "semver",
            "--version-scheme",
            "pep440",
        )

    assert git.tag_exist("0.2.0a0") is True


@pytest.mark.parametrize(
    ("arg", "cfg", "expected"),
    [
        pytest.param("", "", "default", id="default"),
        pytest.param("", "changelog.cfg", "from config", id="from-config"),
        pytest.param(
            "--template=changelog.cmd", "changelog.cfg", "from cmd", id="from-command"
        ),
    ],
)
def test_bump_template_option_precedence(
    tmp_commitizen_project: Path,
    util: UtilFixture,
    any_changelog_format: ChangelogFormat,
    arg: str,
    cfg: str,
    expected: str,
):
    project_root = Path(tmp_commitizen_project)
    cfg_template = project_root / "changelog.cfg"
    cmd_template = project_root / "changelog.cmd"
    default_template = project_root / any_changelog_format.template
    changelog = project_root / any_changelog_format.default_changelog_file

    cfg_template.write_text("from config")
    cmd_template.write_text("from cmd")
    default_template.write_text("default")

    util.create_file_and_commit("feat: new file")

    if cfg:
        pyproject = project_root / "pyproject.toml"
        pyproject.write_text(
            dedent(
                f"""\
                [tool.commitizen]
                version = "0.1.0"
                template = "{cfg}"
                """
            )
        )

    args = ["bump", "--yes", "--changelog"]
    if arg:
        args.append(arg)
    args.append("0.1.1")
    util.run_cli(*args)

    assert changelog.read_text() == expected


def test_bump_template_extras_precedence(
    tmp_commitizen_project: Path,
    util: UtilFixture,
    any_changelog_format: ChangelogFormat,
    mock_plugin: BaseCommitizen,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("{{first}} - {{second}} - {{third}}")

    mock_plugin.template_extras = dict(
        first="from-plugin", second="from-plugin", third="from-plugin"
    )

    pyproject = project_root / "pyproject.toml"
    pyproject.write_text(
        dedent(
            """\
            [tool.commitizen]
            version = "0.1.0"
            [tool.commitizen.extras]
            first = "from-config"
            second = "from-config"
            """
        )
    )

    util.create_file_and_commit("feat: new file")

    util.run_cli(
        "bump",
        "--yes",
        "--changelog",
        "--extra",
        "first=from-command",
        "0.1.1",
    )

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == "from-command - from-config - from-plugin"


def test_bump_template_extra_quotes(
    tmp_commitizen_project: Path,
    util: UtilFixture,
    any_changelog_format: ChangelogFormat,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("{{first}} - {{second}} - {{third}}")

    util.create_file_and_commit("feat: new file")

    util.run_cli(
        "bump",
        "--changelog",
        "--yes",
        "-e",
        "first=no-quote",
        "-e",
        "second='single quotes'",
        "-e",
        'third="double quotes"',
        "0.1.1",
    )

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == "no-quote - single quotes - double quotes"


def test_bump_changelog_contains_increment_only(
    tmp_commitizen_project: Path, util: UtilFixture, capsys: pytest.CaptureFixture
):
    """Issue 1024"""
    # Initialize commitizen up to v1.0.0
    project_root = Path(tmp_commitizen_project)
    tmp_commitizen_cfg_file = project_root / "pyproject.toml"
    tmp_commitizen_cfg_file.write_text(
        '[tool.commitizen]\nversion="1.0.0"\nupdate_changelog_on_bump = true\n'
    )
    tmp_changelog_file = project_root / "CHANGELOG.md"
    tmp_changelog_file.write_text("## v1.0.0")
    util.create_file_and_commit("feat(user): new file")
    util.create_tag("v1.0.0")

    # Add a commit and bump to v2.0.0
    util.create_file_and_commit("feat(user)!: new file")
    util.run_cli("bump", "--yes")
    _ = capsys.readouterr()

    # Add a commit and create the incremental changelog to v3.0.0
    # it should only include v3 changes
    util.create_file_and_commit("feat(next)!: next version")
    with pytest.raises(ExpectedExit):
        util.run_cli("bump", "--yes", "--version-files-only", "--changelog-to-stdout")
    out, _ = capsys.readouterr()

    assert "3.0.0" in out
    assert "2.0.0" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_get_next(util: UtilFixture, capsys: pytest.CaptureFixture):
    util.create_file_and_commit("feat: new file")

    with pytest.raises(DryRunExit):
        util.run_cli("bump", "--yes", "--get-next")

    out, _ = capsys.readouterr()
    assert "0.2.0" in out
    assert git.tag_exist("0.2.0") is False


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_get_next_update_changelog_on_bump(
    util: UtilFixture, capsys: pytest.CaptureFixture, config_path: Path
):
    util.create_file_and_commit("feat: new file")
    with config_path.open("a", encoding="utf-8") as fp:
        fp.write("update_changelog_on_bump = true\n")

    with pytest.raises(DryRunExit):
        util.run_cli("bump", "--yes", "--get-next")

    out, _ = capsys.readouterr()
    assert "0.2.0" in out
    assert git.tag_exist("0.2.0") is False


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_get_next__no_eligible_commits_raises(util: UtilFixture):
    util.create_file_and_commit("chore: new commit")

    with pytest.raises(NoneIncrementExit):
        util.run_cli("bump", "--yes", "--get-next")


def test_bump_allow_no_commit_with_no_commit(
    tmp_commitizen_project, util: UtilFixture, capsys
):
    with tmp_commitizen_project.as_cwd():
        # Create the first commit and bump to 1.0.0
        util.create_file_and_commit("feat(user)!: new file")
        util.run_cli("bump", "--yes")

        # Verify NoCommitsFoundError should be raised
        # when there's no new commit and "--allow-no-commit" is not set
        with pytest.raises(NoCommitsFoundError):
            util.run_cli("bump")

        # bump to 1.0.1 with new commit when "--allow-no-commit" is set
        util.run_cli("bump", "--allow-no-commit")
        out, _ = capsys.readouterr()
        assert "bump: version 1.0.0 → 1.0.1" in out


def test_bump_allow_no_commit_with_no_eligible_commit(
    tmp_commitizen_project, util: UtilFixture, capsys
):
    with tmp_commitizen_project.as_cwd():
        # Create the first commit and bump to 1.0.0
        util.create_file_and_commit("feat(user)!: new file")
        util.run_cli("bump", "--yes")

        # Create a commit that is ineligible to bump
        util.create_file_and_commit("docs(bump): add description for allow no commit")

        # Verify NoneIncrementExit should be raised
        # when there's no eligible bumping commit and "--allow-no-commit" is not set
        with pytest.raises(NoneIncrementExit):
            util.run_cli("bump", "--yes")

        # bump to 1.0.1 with ineligible commit when "--allow-no-commit" is set
        util.run_cli("bump", "--allow-no-commit")
        out, _ = capsys.readouterr()
        assert "bump: version 1.0.0 → 1.0.1" in out


def test_bump_allow_no_commit_with_increment(
    tmp_commitizen_project, util: UtilFixture, capsys
):
    with tmp_commitizen_project.as_cwd():
        # # Create the first commit and bump to 1.0.0
        util.create_file_and_commit("feat(user)!: new file")
        util.run_cli("bump", "--yes")

        # Verify NoCommitsFoundError should be raised
        # when there's no new commit and "--allow-no-commit" is not set
        with pytest.raises(NoCommitsFoundError):
            util.run_cli("bump", "--yes")

        # bump to 1.1.0 with no new commit when "--allow-no-commit" is set
        # and increment is specified
        util.run_cli("bump", "--yes", "--allow-no-commit", "--increment", "MINOR")
        out, _ = capsys.readouterr()
        assert "bump: version 1.0.0 → 1.1.0" in out


def test_bump_allow_no_commit_with_manual_version(
    tmp_commitizen_project, util: UtilFixture, capsys
):
    with tmp_commitizen_project.as_cwd():
        # # Create the first commit and bump to 1.0.0
        util.create_file_and_commit("feat(user)!: new file")
        util.run_cli("bump", "--yes")

        # Verify NoCommitsFoundError should be raised
        # when there's no new commit and "--allow-no-commit" is not set
        with pytest.raises(NoCommitsFoundError):
            util.run_cli("bump", "--yes")

        # bump to 1.1.0 with no new commit when "--allow-no-commit" is set
        # and increment is specified
        util.run_cli("bump", "--yes", "--allow-no-commit", "2.0.0")
        out, _ = capsys.readouterr()
        assert "bump: version 1.0.0 → 2.0.0" in out


def test_bump_detect_legacy_tags_from_scm(
    tmp_commitizen_project: py.path.local, util: UtilFixture
):
    project_root = Path(tmp_commitizen_project)
    tmp_commitizen_cfg_file = project_root / "pyproject.toml"
    tmp_commitizen_cfg_file.write_text(
        "\n".join(
            [
                "[tool.commitizen]",
                'version_provider = "scm"',
                'tag_format = "v$version"',
                "legacy_tag_formats = [",
                '  "legacy-${version}"',
                "]",
            ]
        ),
    )
    util.create_file_and_commit("feat: new file")
    util.create_tag("legacy-0.4.2")
    util.create_file_and_commit("feat: new file")

    util.run_cli("bump", "--increment", "patch", "--changelog")

    assert git.tag_exist("v0.4.3") is True


def test_bump_warn_but_dont_fail_on_invalid_tags(
    tmp_commitizen_project: py.path.local,
    util: UtilFixture,
    capsys: pytest.CaptureFixture,
):
    project_root = Path(tmp_commitizen_project)
    tmp_commitizen_cfg_file = project_root / "pyproject.toml"
    tmp_commitizen_cfg_file.write_text(
        "\n".join(
            [
                "[tool.commitizen]",
                'version_provider = "scm"',
                'version_scheme = "pep440"',
            ]
        ),
    )
    util.create_file_and_commit("feat: new file")
    util.create_tag("0.4.2")
    util.create_file_and_commit("feat: new file")
    util.create_tag("0.4.3.deadbeaf")
    util.create_file_and_commit("feat: new file")

    util.run_cli("bump", "--increment", "patch", "--changelog")

    _, err = capsys.readouterr()

    assert err.count("Invalid version tag: '0.4.3.deadbeaf'") == 1
    assert git.tag_exist("0.4.3") is True


def test_is_initial_tag(mocker: MockFixture, tmp_commitizen_project, util: UtilFixture):
    """Test the _is_initial_tag method behavior."""
    # Create a commit but no tags
    util.create_file_and_commit("feat: initial commit")

    # Initialize Bump with minimal config
    config = BaseConfig()
    config.settings.update(
        {
            "name": defaults.DEFAULT_SETTINGS["name"],
            "encoding": "utf-8",
            "pre_bump_hooks": [],
            "post_bump_hooks": [],
        }
    )

    # Initialize with required arguments
    arguments = {
        "changelog": False,
        "changelog_to_stdout": False,
        "git_output_to_stderr": False,
        "no_verify": False,
        "check_consistency": False,
        "retry": False,
        "version_scheme": None,
        "file_name": None,
        "template": None,
        "extras": None,
    }

    bump_cmd = bump.Bump(config, arguments)  # type: ignore[arg-type]

    # Test case 1: No current tag, not yes mode
    mocker.patch("questionary.confirm", return_value=mocker.Mock(ask=lambda: True))
    assert bump_cmd._is_initial_tag(None, is_yes=False) is True

    # Test case 2: No current tag, yes mode
    assert bump_cmd._is_initial_tag(None, is_yes=True) is True

    # Test case 3: Has current tag
    mock_tag = mocker.Mock()
    assert bump_cmd._is_initial_tag(mock_tag, is_yes=False) is False

    # Test case 4: No current tag, user denies
    mocker.patch("questionary.confirm", return_value=mocker.Mock(ask=lambda: False))
    assert bump_cmd._is_initial_tag(None, is_yes=False) is False


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2025-01-01")
def test_changelog_config_flag_merge_prerelease(
    mocker: MockFixture,
    util: UtilFixture,
    changelog_path: Path,
    config_path: Path,
    file_regression: FileRegressionFixture,
    test_input: str,
):
    with config_path.open("a") as f:
        f.write("changelog_merge_prerelease = true\n")
        f.write("update_changelog_on_bump = true\n")
        f.write("annotated_tag = true\n")

    util.create_file_and_commit("irrelevant commit")
    mocker.patch("commitizen.git.GitTag.date", "1970-01-01")
    git.tag("0.1.0")

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")
    util.run_cli("bump", "--prerelease", test_input, "--yes")

    util.run_cli("bump", "--changelog")

    out = changelog_path.read_text()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2025-01-01")
def test_changelog_config_flag_merge_prerelease_only_prerelease_present(
    util: UtilFixture,
    changelog_path: Path,
    config_path: Path,
    file_regression: FileRegressionFixture,
    test_input: str,
):
    with config_path.open("a") as f:
        f.write("changelog_merge_prerelease = true\n")
        f.write("update_changelog_on_bump = true\n")
        f.write("annotated_tag = true\n")

    util.create_file_and_commit("feat: more relevant commit")
    util.run_cli("bump", "--prerelease", test_input, "--yes")

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")
    util.run_cli("bump", "--prerelease", test_input, "--yes")

    util.run_cli("bump", "--changelog")

    out = changelog_path.read_text()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_deprecate_files_only(util: UtilFixture):
    util.create_file_and_commit("feat: new file")
    with (
        pytest.warns(DeprecationWarning, match=r".*--files-only.*deprecated"),
        pytest.raises(ExpectedExit),
    ):
        util.run_cli("bump", "--yes", "--files-only")


@pytest.mark.parametrize(
    ("prerelease", "merge"),
    [
        pytest.param(True, "true", id="with_prerelease_merge"),
        pytest.param(True, "false", id="with_prerelease_no_merge"),
        pytest.param(False, "true", id="without_prerelease"),
    ],
)
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2025-01-01")
def test_changelog_merge_preserves_header(
    mocker: MockFixture,
    util: UtilFixture,
    changelog_path: Path,
    config_path: Path,
    file_regression: FileRegressionFixture,
    prerelease: bool,
    merge: str,
):
    """Test that merge_prerelease preserves existing changelog header."""
    with config_path.open("a") as f:
        f.write(f"changelog_merge_prerelease = {merge}\n")
        f.write("update_changelog_on_bump = true\n")
        f.write("annotated_tag = true\n")

    # Create initial version with changelog that has a header
    util.create_file_and_commit("irrelevant commit")
    mocker.patch("commitizen.git.GitTag.date", "1970-01-01")
    git.tag("0.1.0")

    # Create a changelog with a header manually
    changelog_path.write_text(
        dedent("""\
            # Changelog

            All notable changes to this project will be documented here.

            ## 0.1.0 (1970-01-01)
            """)
    )

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")

    if prerelease:
        util.run_cli("bump", "--prerelease", "alpha", "--yes")

    util.create_file_and_commit("feat: new feature right before the bump")
    util.run_cli("bump", "--changelog")

    out = changelog_path.read_text()

    file_regression.check(out, extension=".md")
