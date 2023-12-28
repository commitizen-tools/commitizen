from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockFixture

import commitizen.commands.bump as bump
from commitizen import cli, cmd, git, hooks
from commitizen.cz.base import BaseCommitizen
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
from commitizen.changelog_formats import ChangelogFormat
from tests.utils import create_file_and_commit, create_tag


@pytest.mark.parametrize(
    "commit_msg",
    (
        "fix: username exception",
        "fix(user): username exception",
        "refactor: remove ini configuration support",
        "refactor(config): remove ini configuration support",
        "perf: update to use multiproess",
        "perf(worker): update to use multiproess",
    ),
)
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_patch_increment(commit_msg, mocker: MockFixture):
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.1.1")
    assert tag_exists is True


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_minor_increment(commit_msg, mocker: MockFixture):
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "commit:refs/tags/0.2.0\n" in cmd_res.out


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_minor_increment_annotated(commit_msg, mocker: MockFixture):
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes", "--annotated-tag"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "tag:refs/tags/0.2.0\n" in cmd_res.out

    _is_signed = git.is_signed_tag("0.2.0")
    assert _is_signed is False


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
@pytest.mark.usefixtures("tmp_commitizen_project_with_gpg")
def test_bump_minor_increment_signed(commit_msg, mocker: MockFixture):
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes", "--gpg-sign"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "tag:refs/tags/0.2.0\n" in cmd_res.out

    _is_signed = git.is_signed_tag("0.2.0")
    assert _is_signed is True


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
def test_bump_minor_increment_annotated_config_file(
    commit_msg, mocker: MockFixture, tmp_commitizen_project
):
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write(
        f"{tmp_commitizen_cfg_file.read()}\n" f"annotated_tag = 1"
    )
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "tag:refs/tags/0.2.0\n" in cmd_res.out

    _is_signed = git.is_signed_tag("0.2.0")
    assert _is_signed is False


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
def test_bump_minor_increment_signed_config_file(
    commit_msg, mocker: MockFixture, tmp_commitizen_project_with_gpg
):
    tmp_commitizen_cfg_file = tmp_commitizen_project_with_gpg.join("pyproject.toml")
    tmp_commitizen_cfg_file.write(f"{tmp_commitizen_cfg_file.read()}\n" f"gpg_sign = 1")
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "tag:refs/tags/0.2.0\n" in cmd_res.out

    _is_signed = git.is_signed_tag("0.2.0")
    assert _is_signed is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "commit_msg",
    (
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface",
        "feat(user): new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface",
        "BREAKING CHANGE: age is no longer supported",
        "BREAKING-CHANGE: age is no longer supported",
    ),
)
def test_bump_major_increment(commit_msg, mocker: MockFixture):
    create_file_and_commit(commit_msg)

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("1.0.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "commit_msg",
    (
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface",
        "feat(user): new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface",
        "BREAKING CHANGE: age is no longer supported",
        "BREAKING-CHANGE: age is no longer supported",
    ),
)
def test_bump_major_increment_major_version_zero(commit_msg, mocker):
    create_file_and_commit(commit_msg)

    testargs = ["cz", "bump", "--yes", "--major-version-zero"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "commit_msg,increment,expected_tag",
    [
        ("feat: new file", "PATCH", "0.1.1"),
        ("fix: username exception", "major", "1.0.0"),
        ("refactor: remove ini configuration support", "patch", "0.1.1"),
        ("BREAKING CHANGE: age is no longer supported", "minor", "0.2.0"),
    ],
)
def test_bump_command_increment_option(
    commit_msg, increment, expected_tag, mocker: MockFixture
):
    create_file_and_commit(commit_msg)

    testargs = ["cz", "bump", "--increment", increment, "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist(expected_tag)
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_prelease(mocker: MockFixture):
    create_file_and_commit("feat: location")

    # Create an alpha pre-release.
    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0a0")
    assert tag_exists is True

    # Create a beta pre-release.
    testargs = ["cz", "bump", "--prerelease", "beta", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0b0")
    assert tag_exists is True

    # With a current beta pre-release, bumping alpha must bump beta
    # because we can't bump "backwards".
    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0a1")
    assert tag_exists is False
    tag_exists = git.tag_exist("0.2.0b1")
    assert tag_exists is True

    # Create a rc pre-release.
    testargs = ["cz", "bump", "--prerelease", "rc", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0rc0")
    assert tag_exists is True

    # With a current rc pre-release, bumping alpha must bump rc.
    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0a1")
    assert tag_exists is False
    tag_exists = git.tag_exist("0.2.0b2")
    assert tag_exists is False
    tag_exists = git.tag_exist("0.2.0rc1")
    assert tag_exists is True

    # With a current rc pre-release, bumping beta must bump rc.
    testargs = ["cz", "bump", "--prerelease", "beta", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0a2")
    assert tag_exists is False
    tag_exists = git.tag_exist("0.2.0b2")
    assert tag_exists is False
    tag_exists = git.tag_exist("0.2.0rc2")
    assert tag_exists is True

    # Create a final release from the current pre-release.
    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_prelease_increment(mocker: MockFixture):
    # FINAL RELEASE
    create_file_and_commit("fix: location")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    assert git.tag_exist("0.1.1")

    # PRERELEASE
    create_file_and_commit("fix: location")

    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    assert git.tag_exist("0.1.2a0")

    create_file_and_commit("feat: location")

    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    assert git.tag_exist("0.2.0a0")

    create_file_and_commit("feat!: breaking")

    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    assert git.tag_exist("1.0.0a0")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_on_git_with_hooks_no_verify_disabled(mocker: MockFixture):
    """Bump commit without --no-verify"""
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/pre-commit", "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n" 'echo "0.1.0"')
    cmd.run("chmod +x .git/hooks/pre-commit")

    # MINOR
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_tag_exists_raises_exception(mocker: MockFixture):
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/post-commit", "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n" "exit 9")
    cmd.run("chmod +x .git/hooks/post-commit")

    # MINOR
    create_file_and_commit("feat: new file")
    git.tag("0.2.0")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(BumpTagFailedError) as excinfo:
        cli.main()
    assert "0.2.0" in str(excinfo.value)  # This should be a fatal error


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_on_git_with_hooks_no_verify_enabled(mocker: MockFixture):
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/pre-commit", "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n" 'echo "0.1.0"')
    cmd.run("chmod +x .git/hooks/pre-commit")

    # MINOR
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", "--no-verify"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_when_bumpping_is_not_support(mocker: MockFixture):
    create_file_and_commit(
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported"
    )

    testargs = ["cz", "-n", "cz_jira", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoPatternMapError) as excinfo:
        cli.main()

    assert "'cz_jira' rule does not support bump" in str(excinfo.value)


@pytest.mark.usefixtures("tmp_git_project")
def test_bump_when_version_is_not_specify(mocker: MockFixture):
    mocker.patch.object(sys, "argv", ["cz", "bump"])

    with pytest.raises(NoVersionSpecifiedError) as excinfo:
        cli.main()

    assert NoVersionSpecifiedError.message in str(excinfo.value)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_when_no_new_commit(mocker: MockFixture):
    """bump without any commits since the last bump."""
    # We need this first commit otherwise the revision is invalid.
    create_file_and_commit("feat: initial")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    # First bump.
    # The next bump should fail since
    # there is not a commit between the two bumps.
    cli.main()

    # bump without a new commit.
    with pytest.raises(NoCommitsFoundError) as excinfo:
        cli.main()

    expected_error_message = "[NO_COMMITS_FOUND]\n" "No new commits found."
    assert expected_error_message in str(excinfo.value)


def test_bump_when_version_inconsistent_in_version_files(
    tmp_commitizen_project, mocker: MockFixture
):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("100.999.10000")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
    tmp_commitizen_cfg_file.write(
        f"{tmp_commitizen_cfg_file.read()}\n"
        f'version_files = ["{tmp_version_file_string}"]'
    )

    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", "--check-consistency"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(CurrentVersionNotFoundError) as excinfo:
        cli.main()

    partial_expected_error_message = "Current version 0.1.0 is not found in"
    assert partial_expected_error_message in str(excinfo.value)


def test_bump_major_version_zero_when_major_is_not_zero(mocker, tmp_commitizen_project):
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

    create_file_and_commit("feat(user): new file")
    create_tag("v1.0.0")
    create_file_and_commit("feat(user)!: new file")

    testargs = ["cz", "bump", "--yes", "--major-version-zero"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NotAllowed) as excinfo:
        cli.main()

    expected_error_message = (
        "--major-version-zero is meaningless for current version 1.0.0"
    )
    assert expected_error_message in str(excinfo.value)


def test_bump_files_only(mocker: MockFixture, tmp_commitizen_project):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("0.1.0")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
    tmp_commitizen_cfg_file.write(
        f"{tmp_commitizen_cfg_file.read()}\n"
        f'version_files = ["{tmp_version_file_string}"]'
    )

    create_file_and_commit("feat: new user interface")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    create_file_and_commit("feat: another new feature")
    testargs = ["cz", "bump", "--yes", "--files-only"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(ExpectedExit):
        cli.main()

    tag_exists = git.tag_exist("0.3.0")
    assert tag_exists is False

    with open(tmp_version_file, encoding="utf-8") as f:
        assert "0.3.0" in f.read()

    with open(tmp_commitizen_cfg_file, encoding="utf-8") as f:
        assert "0.3.0" in f.read()


def test_bump_local_version(mocker: MockFixture, tmp_commitizen_project):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("4.5.1+0.1.0")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
    tmp_commitizen_cfg_file.write(
        f"[tool.commitizen]\n"
        'version="4.5.1+0.1.0"\n'
        f'version_files = ["{tmp_version_file_string}"]'
    )

    create_file_and_commit("feat: new user interface")
    testargs = ["cz", "bump", "--yes", "--local-version"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("4.5.1+0.2.0")
    assert tag_exists is True

    with open(tmp_version_file, encoding="utf-8") as f:
        assert "4.5.1+0.2.0" in f.read()


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_dry_run(mocker: MockFixture, capsys):
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()

    out, _ = capsys.readouterr()
    assert "0.2.0" in out

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is False


def test_bump_in_non_git_project(tmpdir, config, mocker: MockFixture):
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            with pytest.raises(ExpectedExit):
                cli.main()


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
):
    create_file_and_commit("test(test_get_all_droplets): fix bad comparison test")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    # stash git.tag for later restore
    stashed_git_tag = git.tag
    dummy_value = git.tag("0.0.2")
    git.tag = MagicMock(return_value=dummy_value)

    with pytest.raises(NoneIncrementExit):
        try:
            cli.main()
        except NoneIncrementExit as e:
            git.tag.assert_not_called()
            assert e.exit_code == ExitCode.NO_INCREMENT
            raise e

    # restore pop stashed
    git.tag = stashed_git_tag


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_arg(mocker: MockFixture, changelog_path):
    create_file_and_commit("feat(user): new file")
    testargs = ["cz", "bump", "--yes", "--changelog"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()
    assert out.startswith("#")
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_config(mocker: MockFixture, changelog_path, config_path):
    create_file_and_commit("feat(user): new file")
    with open(config_path, "a", encoding="utf-8") as fp:
        fp.write("update_changelog_on_bump = true\n")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()
    assert out.startswith("#")
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_prevent_prerelease_when_no_increment_detected(mocker: MockFixture, capsys):
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()
    out, _ = capsys.readouterr()

    assert "0.2.0" in out

    create_file_and_commit("test: new file")
    testargs = ["cz", "bump", "-pr", "beta"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoCommitsFoundError) as excinfo:
        cli.main()

    expected_error_message = (
        "[NO_COMMITS_FOUND]\n" "No commits found to generate a pre-release."
    )
    assert expected_error_message in str(excinfo.value)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_to_stdout_arg(mocker: MockFixture, capsys, changelog_path):
    create_file_and_commit("feat(user): this should appear in stdout")
    testargs = ["cz", "bump", "--yes", "--changelog-to-stdout"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    out, _ = capsys.readouterr()

    assert "this should appear in stdout" in out
    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()
    assert out.startswith("#")
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_changelog_to_stdout_dry_run_arg(
    mocker: MockFixture, capsys, changelog_path
):
    create_file_and_commit(
        "feat(user): this should appear in stdout with dry-run enabled"
    )
    testargs = ["cz", "bump", "--yes", "--changelog-to-stdout", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is False
    assert out.startswith("#")
    assert "this should appear in stdout with dry-run enabled" in out
    assert "0.2.0" in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_without_git_to_stdout_arg(mocker: MockFixture, capsys, changelog_path):
    create_file_and_commit("feat(user): this should appear in stdout")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    out, _ = capsys.readouterr()

    assert (
        re.search(r"^\[master \w+] bump: version 0.1.0 → 0.2.0", out, re.MULTILINE)
        is not None
    )


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_with_git_to_stdout_arg(mocker: MockFixture, capsys, changelog_path):
    create_file_and_commit("feat(user): this should appear in stdout")
    testargs = ["cz", "bump", "--yes", "--git-output-to-stderr"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    out, _ = capsys.readouterr()

    assert (
        re.search(r"^\[master \w+] bump: version 0.1.0 → 0.2.0", out, re.MULTILINE)
        is None
    )


@pytest.mark.parametrize(
    "version_filepath, version_regex, version_file_content",
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
    ],
)
@pytest.mark.parametrize(
    "cli_bump_changelog_args",
    [
        ("cz", "bump", "--changelog", "--yes"),
        (
            "cz",
            "bump",
            "--changelog",
            "--changelog-to-stdout",
            "--annotated-tag",
            "--check-consistency",
            "--yes",
        ),
    ],
    ids=lambda cmd_tuple: " ".join(cmd_tuple),
)
def test_bump_changelog_command_commits_untracked_changelog_and_version_files(
    tmp_commitizen_project,
    mocker,
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
        commitizen_config.write(f"version_files = [\n" f"'{version_regex}'\n]")

    with tmp_commitizen_project.join(version_filepath).open(
        mode="a+", encoding="utf-8"
    ) as version_file:
        version_file.write(version_file_content)

    create_file_and_commit("fix: some test commit")

    mocker.patch.object(sys, "argv", cli_bump_changelog_args)
    cli.main()

    commit_file_names = git.get_filenames_in_commit()
    assert "CHANGELOG.md" in commit_file_names
    assert version_filepath in commit_file_names


@pytest.mark.parametrize(
    "testargs",
    [
        ["cz", "bump", "--local-version", "1.2.3"],
        ["cz", "bump", "--prerelease", "rc", "1.2.3"],
        ["cz", "bump", "--devrelease", "0", "1.2.3"],
        ["cz", "bump", "--devrelease", "1", "1.2.3"],
        ["cz", "bump", "--increment", "PATCH", "1.2.3"],
        ["cz", "bump", "--build-metadata=a.b.c", "1.2.3"],
        ["cz", "bump", "--local-version", "--build-metadata=a.b.c"],
    ],
)
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_invalid_manual_args_raises_exception(mocker, testargs):
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NotAllowed):
        cli.main()


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "manual_version",
    [
        "noversion",
        "1.2..3",
    ],
)
def test_bump_invalid_manual_version_raises_exception(mocker, manual_version):
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", manual_version]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(InvalidManualVersion) as excinfo:
        cli.main()

    expected_error_message = (
        "[INVALID_MANUAL_VERSION]\n" f"Invalid manual version: '{manual_version}'"
    )
    assert expected_error_message in str(excinfo.value)


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
    ],
)
def test_bump_manual_version(mocker, manual_version):
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", manual_version]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist(manual_version)
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_manual_version_disallows_major_version_zero(mocker):
    create_file_and_commit("feat: new file")

    manual_version = "0.2.0"
    testargs = ["cz", "bump", "--yes", "--major-version-zero", manual_version]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NotAllowed) as excinfo:
        cli.main()

    expected_error_message = (
        "--major-version-zero cannot be combined with MANUAL_VERSION"
    )
    assert expected_error_message in str(excinfo.value)


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
def test_bump_with_pre_bump_hooks(
    commit_msg, mocker: MockFixture, tmp_commitizen_project
):
    pre_bump_hook = "scripts/pre_bump_hook.sh"
    post_bump_hook = "scripts/post_bump_hook.sh"

    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write(
        f"{tmp_commitizen_cfg_file.read()}\n"
        f'pre_bump_hooks = ["{pre_bump_hook}"]\n'
        f'post_bump_hooks = ["{post_bump_hook}"]\n'
    )

    run_mock = mocker.Mock()
    mocker.patch.object(hooks, "run", run_mock)

    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

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


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_manual_version_disallows_prerelease_offset(mocker):
    create_file_and_commit("feat: new file")

    manual_version = "0.2.0"
    testargs = ["cz", "bump", "--yes", "--prerelease-offset", "42", manual_version]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NotAllowed) as excinfo:
        cli.main()

    expected_error_message = (
        "--prerelease-offset cannot be combined with MANUAL_VERSION"
    )
    assert expected_error_message in str(excinfo.value)


@pytest.mark.usefixtures("tmp_git_project")
def test_bump_use_version_provider(mocker: MockFixture):
    mock = mocker.MagicMock(name="provider")
    mock.get_version.return_value = "0.0.0"
    get_provider = mocker.patch(
        "commitizen.commands.bump.get_provider", return_value=mock
    )

    create_file_and_commit("fix: fake commit")
    testargs = ["cz", "bump", "--yes", "--changelog"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()

    assert git.tag_exist("0.0.1")
    get_provider.assert_called_once()
    mock.get_version.assert_called_once()
    mock.set_version.assert_called_once_with("0.0.1")


def test_bump_command_prelease_scheme_via_cli(
    tmp_commitizen_project_initial, mocker: MockFixture
):
    tmp_commitizen_project = tmp_commitizen_project_initial()
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")

    testargs = [
        "cz",
        "bump",
        "--prerelease",
        "alpha",
        "--yes",
        "--version-scheme",
        "semver",
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0-a0")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0-a0" in f.read()

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0" in f.read()


def test_bump_command_prelease_scheme_via_config(
    tmp_commitizen_project_initial, mocker: MockFixture
):
    tmp_commitizen_project = tmp_commitizen_project_initial(
        config_extra='version_scheme = "semver"\n',
    )
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")

    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0-a0")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0-a0" in f.read()

    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0-a1")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0-a1" in f.read()

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0" in f.read()


def test_bump_command_prelease_scheme_check_old_tags(
    tmp_commitizen_project_initial, mocker: MockFixture
):
    tmp_commitizen_project = tmp_commitizen_project_initial(
        config_extra=('tag_format = "v$version"\nversion_scheme = "semver"\n'),
    )
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")

    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("v0.2.0-a0")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0-a0" in f.read()

    testargs = ["cz", "bump", "--prerelease", "alpha"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("v0.2.0-a1")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0-a1" in f.read()

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("v0.2.0")
    assert tag_exists is True

    for version_file in [tmp_version_file, tmp_commitizen_cfg_file]:
        with open(version_file) as f:
            assert "0.2.0" in f.read()


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.usefixtures("use_cz_semver")
@pytest.mark.parametrize(
    "message, expected_tag",
    [
        ("minor: add users", "0.2.0"),
        ("patch: bug affecting users", "0.1.1"),
        ("major: bug affecting users", "1.0.0"),
    ],
)
def test_bump_with_plugin(mocker: MockFixture, message: str, expected_tag: str):
    create_file_and_commit(message)

    testargs = ["cz", "--name", "cz_semver", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist(expected_tag)
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.usefixtures("use_cz_semver")
@pytest.mark.parametrize(
    "message, expected_tag",
    [
        ("minor: add users", "0.2.0"),
        ("patch: bug affecting users", "0.1.1"),
        ("major: bug affecting users", "0.2.0"),
    ],
)
def test_bump_with_major_version_zero_with_plugin(
    mocker: MockFixture, message: str, expected_tag: str
):
    create_file_and_commit(message)

    testargs = ["cz", "--name", "cz_semver", "bump", "--yes", "--major-version-zero"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist(expected_tag)
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_version_type_deprecation(mocker: MockFixture):
    create_file_and_commit("feat: check deprecation on --version-type")

    testargs = [
        "cz",
        "bump",
        "--prerelease",
        "alpha",
        "--yes",
        "--version-type",
        "semver",
    ]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.warns(DeprecationWarning):
        cli.main()

    assert git.tag_exist("0.2.0-a0")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_version_scheme_priority_over_version_type(mocker: MockFixture):
    create_file_and_commit("feat: check deprecation on --version-type")

    testargs = [
        "cz",
        "bump",
        "--prerelease",
        "alpha",
        "--yes",
        "--version-type",
        "semver",
        "--version-scheme",
        "pep440",
    ]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.warns(DeprecationWarning):
        cli.main()

    assert git.tag_exist("0.2.0a0")


@pytest.mark.parametrize(
    "arg, cfg, expected",
    (
        pytest.param("", "", "default", id="default"),
        pytest.param("", "changelog.cfg", "from config", id="from-config"),
        pytest.param(
            "--template=changelog.cmd", "changelog.cfg", "from cmd", id="from-command"
        ),
    ),
)
def test_bump_template_option_precedance(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
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

    create_file_and_commit("feat: new file")

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

    testargs = ["cz", "bump", "--yes", "--changelog"]
    if arg:
        testargs.append(arg)
    mocker.patch.object(sys, "argv", testargs + ["0.1.1"])
    cli.main()

    out = changelog.read_text()
    assert out == expected


def test_bump_template_extras_precedance(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
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

    create_file_and_commit("feat: new file")

    testargs = [
        "cz",
        "bump",
        "--yes",
        "--changelog",
        "--extra",
        "first=from-command",
        "0.1.1",
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == "from-command - from-config - from-plugin"


def test_bump_template_extra_quotes(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("{{first}} - {{second}} - {{third}}")

    create_file_and_commit("feat: new file")

    testargs = [
        "cz",
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
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == "no-quote - single quotes - double quotes"
