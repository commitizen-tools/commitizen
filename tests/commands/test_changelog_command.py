from __future__ import annotations

import itertools
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from jinja2 import FileSystemLoader

from commitizen import git
from commitizen.commands.changelog import Changelog
from commitizen.exceptions import (
    DryRunExit,
    InvalidCommandArgumentError,
    NoCommitsFoundError,
    NoRevisionError,
    NotAGitProjectError,
    NotAllowed,
)

if TYPE_CHECKING:
    from pytest_mock import MockFixture
    from pytest_regressions.file_regression import FileRegressionFixture

    from commitizen.changelog_formats import ChangelogFormat
    from commitizen.config.base_config import BaseConfig
    from commitizen.config.json_config import JsonConfig
    from commitizen.cz.base import BaseCommitizen
    from tests.utils import UtilFixture


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_from_version_zero_point_two(
    capsys: pytest.CaptureFixture,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    util.create_file_and_commit("feat: new file")
    util.create_file_and_commit("refactor: not in changelog")

    # create tag
    util.run_cli("bump", "--yes")
    capsys.readouterr()

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: after 0.2")

    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run", "--start-rev", "0.2.0")

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_with_different_cz(
    capsys: pytest.CaptureFixture,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    util.create_file_and_commit("JRA-34 #comment corrected indent issue")
    util.create_file_and_commit("JRA-35 #time 1w 2d 4h 30m Total work logged")

    with pytest.raises(DryRunExit):
        util.run_cli("-n", "cz_jira", "changelog", "--dry-run")
    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_from_start(
    changelog_format: ChangelogFormat,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    util.create_file_and_commit("feat: new file")
    util.create_file_and_commit("refactor: is in changelog")
    util.create_file_and_commit("Merge into master")
    changelog_file = f"CHANGELOG.{changelog_format.extension}"
    template = f"CHANGELOG.{changelog_format.extension}.j2"

    util.run_cli("changelog", "--file-name", changelog_file, "--template", template)

    with open(changelog_file, encoding="utf-8") as f:
        out = f.read()
    file_regression.check(out, extension=changelog_format.ext)


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-08-14")
def test_changelog_replacing_unreleased_using_incremental(
    changelog_format: ChangelogFormat,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")
    util.create_file_and_commit("Merge into master")
    changelog_file = f"CHANGELOG.{changelog_format.extension}"
    template = f"CHANGELOG.{changelog_format.extension}.j2"

    util.run_cli("changelog", "--file-name", changelog_file, "--template", template)

    util.run_cli("bump", "--yes", "--file-name", changelog_file, "--template", template)

    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli(
        "changelog",
        "--incremental",
        "--file-name",
        changelog_file,
        "--template",
        template,
    )

    with open(changelog_file, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=changelog_format.ext)


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-08-14")
def test_changelog_is_persisted_using_incremental(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")
    util.create_file_and_commit("Merge into master")

    util.run_cli("bump", "--yes")

    util.run_cli("changelog")

    with open(changelog_path, "a", encoding="utf-8") as f:
        f.write("\nnote: this should be persisted using increment\n")

    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog", "--incremental")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_angular_sample(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(
            "# [10.0.0-rc.3](https://github.com/angular/angular/compare/10.0.0-rc.2...10.0.0-rc.3) (2020-04-22)\n"
            "\n"
            "### Bug Fixes"
            "\n"
            "* **common:** format day-periods that cross midnight ([#36611](https://github.com/angular/angular/issues/36611)) ([c6e5fc4](https://github.com/angular/angular/commit/c6e5fc4)), closes [#36566](https://github.com/angular/angular/issues/36566)\n"
        )
    util.create_file_and_commit("irrelevant commit")
    util.create_tag("10.0.0-rc.3")

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")
    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog", "--incremental")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


KEEP_A_CHANGELOG = """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2017-06-20
### Added
- New visual identity by [@tylerfortune8](https://github.com/tylerfortune8).
- Version navigation.

### Changed
- Start using "changelog" over "change log" since it's the common usage.

### Removed
- Section about "changelog" vs "CHANGELOG".

## [0.3.0] - 2015-12-03
### Added
- RU translation from [@aishek](https://github.com/aishek).
"""


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_keep_a_changelog_sample(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(KEEP_A_CHANGELOG)
    util.create_file_and_commit("irrelevant commit")
    util.create_tag("1.0.0")

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")
    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog", "--incremental")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize("dry_run", [True, False])
def test_changelog_hook(
    mocker: MockFixture, config: BaseConfig, dry_run: bool, util: UtilFixture
):
    changelog_hook_mock = mocker.Mock()
    changelog_hook_mock.return_value = "cool changelog hook"

    util.create_file_and_commit("feat: new file")
    util.create_file_and_commit("refactor: is in changelog")
    util.create_file_and_commit("Merge into master")

    config.settings["change_type_order"] = ["Refactor", "Feat"]  # type: ignore[typeddict-unknown-key]
    changelog = Changelog(
        config, {"unreleased_version": None, "incremental": True, "dry_run": dry_run}
    )
    mocker.patch.object(changelog.cz, "changelog_hook", changelog_hook_mock)
    if dry_run:
        with pytest.raises(DryRunExit):
            changelog()
    else:
        changelog()

    full_changelog = (
        "## Unreleased\n\n### Refactor\n\n- is in changelog\n\n### Feat\n\n- new file\n"
    )
    partial_changelog = full_changelog
    if dry_run:
        partial_changelog = ""

    changelog_hook_mock.assert_called_with(full_changelog, partial_changelog)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_hook_customize(
    mocker: MockFixture, config_customize: JsonConfig, util: UtilFixture
):
    changelog_hook_mock = mocker.Mock()
    changelog_hook_mock.return_value = "cool changelog hook"

    util.create_file_and_commit("feat: new file")
    util.create_file_and_commit("refactor: is in changelog")
    util.create_file_and_commit("Merge into master")

    changelog = Changelog(
        config_customize,
        {"unreleased_version": None, "incremental": True, "dry_run": False},
    )
    mocker.patch.object(changelog.cz, "changelog_hook", changelog_hook_mock)
    changelog()
    full_changelog = (
        "## Unreleased\n\n### Refactor\n\n- is in changelog\n\n### Feat\n\n- new file\n"
    )

    changelog_hook_mock.assert_called_with(full_changelog, full_changelog)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_release_hook(
    mocker: MockFixture, config: BaseConfig, util: UtilFixture
):
    def changelog_release_hook(release: dict, tag: git.GitTag) -> dict:
        return release

    for i in range(3):
        util.create_file_and_commit("feat: new file")
        util.create_file_and_commit("refactor: is in changelog")
        util.create_file_and_commit("Merge into master")
        util.create_tag(f"0.{i + 1}.0")

    # changelog = Changelog(config, {})
    changelog = Changelog(
        config, {"unreleased_version": None, "incremental": True, "dry_run": False}
    )
    mocker.patch.object(changelog.cz, "changelog_release_hook", changelog_release_hook)
    spy = mocker.spy(changelog.cz, "changelog_release_hook")
    changelog()

    assert spy.call_count == 3


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_with_non_linear_merges_commit_order(
    mocker: MockFixture, config_customize: JsonConfig, util: UtilFixture
):
    """Test that commits merged non-linearly are correctly ordered in the changelog

    A typical scenario is having two branches from main like so:
    * feat: I will be merged first - (2023-03-01 11:35:51 +0100) |  (branchB)
    | * feat: I will be merged second - (2023-03-01 11:35:22 +0100) |  (branchA)
    |/
    * feat: initial commit - (2023-03-01 11:34:54 +0100) |  (HEAD -> main)

    And merging them, for example in the reverse order they were created on would give the following:
    *   Merge branch 'branchA' - (2023-03-01 11:42:59 +0100) |  (HEAD -> main)
    |\
    | * feat: I will be merged second - (2023-03-01 11:35:22 +0100) |  (branchA)
    * | feat: I will be merged first - (2023-03-01 11:35:51 +0100) |  (branchB)
    |/
    * feat: initial commit - (2023-03-01 11:34:54 +0100) |

    In this case we want the changelog to reflect the topological order of commits,
    i.e. the order in which they were merged into the main branch

    So the above example should result in the following:
    ## Unreleased

    ### Feat
    - I will be merged second
    - I will be merged first
    - initial commit
    """
    changelog_hook_mock = mocker.Mock()
    changelog_hook_mock.return_value = "cool changelog hook"

    util.create_file_and_commit("feat: initial commit")

    main_branch = util.get_current_branch()

    util.create_branch("branchA")
    util.create_branch("branchB")

    util.switch_branch("branchA")
    util.create_file_and_commit("feat: I will be merged second")

    util.switch_branch("branchB")
    util.create_file_and_commit("feat: I will be merged first")

    # Note we merge branches opposite order than author_date
    util.switch_branch(main_branch)
    util.merge_branch("branchB")
    util.merge_branch("branchA")

    changelog = Changelog(
        config_customize,
        {"unreleased_version": None, "incremental": True, "dry_run": False},
    )
    mocker.patch.object(changelog.cz, "changelog_hook", changelog_hook_mock)
    changelog()
    full_changelog = "\
## Unreleased\n\n\
\
### Feat\n\n\
- I will be merged second\n\
- I will be merged first\n\
- initial commit\n"

    changelog_hook_mock.assert_called_with(full_changelog, full_changelog)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_multiple_incremental_do_not_add_new_lines(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    """Test for bug https://github.com/commitizen-tools/commitizen/issues/192"""
    util.create_file_and_commit("feat: add new output")

    util.run_cli("changelog", "--incremental")

    util.create_file_and_commit("fix: output glitch")

    util.run_cli("changelog", "--incremental")

    util.create_file_and_commit("fix: no more explosions")

    util.run_cli("changelog", "--incremental")

    util.create_file_and_commit("feat: add more stuff")

    util.run_cli("changelog", "--incremental")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_newline_separates_new_content_from_old(
    changelog_path: str, util: UtilFixture
):
    """Test for https://github.com/commitizen-tools/commitizen/issues/509"""
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("Pre-existing content that should be kept\n")

    util.create_file_and_commit("feat: add more cat videos")

    util.run_cli("changelog", "--incremental")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    assert (
        out
        == "Pre-existing content that should be kept\n\n## Unreleased\n\n### Feat\n\n- add more cat videos\n"
    )


def test_changelog_without_revision(tmp_commitizen_project, util: UtilFixture):
    changelog_file = tmp_commitizen_project.join("CHANGELOG.md")
    changelog_file.write(
        """
        # Unreleased

        ## v1.0.0
        """
    )

    with pytest.raises(NoRevisionError):
        util.run_cli("changelog", "--incremental")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_with_revision(util: UtilFixture):
    """combining incremental with a revision doesn't make sense"""
    with pytest.raises(NotAllowed):
        util.run_cli("changelog", "--incremental", "0.2.0")


def test_changelog_with_different_tag_name_and_changelog_content(
    tmp_commitizen_project, util: UtilFixture
):
    changelog_file = tmp_commitizen_project.join("CHANGELOG.md")
    changelog_file.write(
        """
        # Unreleased

        ## v1.0.0
        """
    )
    util.create_file_and_commit("feat: new file")
    util.create_tag("2.0.0")

    with pytest.raises(NoRevisionError):
        util.run_cli("changelog", "--incremental")


@pytest.mark.usefixtures("chdir")
def test_changelog_in_non_git_project(util: UtilFixture):
    with pytest.raises(NotAGitProjectError):
        util.run_cli("changelog", "--incremental")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_beta(
    capsys: pytest.CaptureFixture,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    commit_message = (
        "feat(users): email pattern corrected\n\n"
        "BREAKING CHANGE: migrate by renaming user to users\n\n"
        "footer content"
    )
    util.create_file_and_commit(commit_message)
    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run")
    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1(
    capsys: pytest.CaptureFixture,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    commit_message = (
        "feat(users): email pattern corrected\n\n"
        "body content\n\n"
        "BREAKING CHANGE: migrate by renaming user to users"
    )
    util.create_file_and_commit(commit_message)
    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run")
    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_multiline(
    capsys: pytest.CaptureFixture,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    commit_message = (
        "feat(users): email pattern corrected\n\n"
        "body content\n\n"
        "BREAKING CHANGE: migrate by renaming user to users.\n"
        "and then connect the thingy with the other thingy\n\n"
        "footer content"
    )
    util.create_file_and_commit(commit_message)
    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run")
    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_with_exclamation_mark(
    capsys: pytest.CaptureFixture,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    commit_message = "chore!: drop support for py36"
    util.create_file_and_commit(commit_message)
    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run")
    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_with_exclamation_mark_feat(
    capsys: pytest.CaptureFixture,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    commit_message = "feat(pipeline)!: some text with breaking change"
    util.create_file_and_commit(commit_message)
    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run")
    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_config_flag_increment(
    changelog_path: str,
    config_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write("changelog_incremental = true\n")
    with open(changelog_path, "a", encoding="utf-8") as f:
        f.write("\nnote: this should be persisted using increment\n")

    util.create_file_and_commit("feat: add new output")

    util.run_cli("changelog")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    assert "this should be persisted using increment" in out
    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2025-12-29")
def test_changelog_config_flag_merge_prerelease(
    changelog_path: str,
    config_path: str,
    file_regression: FileRegressionFixture,
    test_input: str,
    util: UtilFixture,
):
    with open(config_path, "a") as f:
        f.write("changelog_merge_prerelease = true\n")

    util.create_file_and_commit("irrelevant commit")
    util.create_tag("1.0.0")

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")

    util.run_cli("bump", "--prerelease", test_input, "--yes")

    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog")

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_config_start_rev_option(
    capsys: pytest.CaptureFixture,
    config_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")
    capsys.readouterr()

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: after 0.2")

    with open(config_path, "a", encoding="utf-8") as f:
        f.write('changelog_start_rev = "0.2.0"\n')

    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run")

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_keep_a_changelog_sample_with_annotated_tag(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    """Fix #378"""
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(KEEP_A_CHANGELOG)
    util.create_file_and_commit("irrelevant commit")
    util.create_tag("1.0.0", annotated=True)

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")
    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog", "--incremental")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2021-06-11")
def test_changelog_incremental_with_release_candidate_version(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    test_input: str,
    util: UtilFixture,
):
    """Fix #357"""
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(KEEP_A_CHANGELOG)
    util.create_file_and_commit("irrelevant commit")
    util.create_tag("1.0.0", annotated=True)

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")

    util.run_cli("bump", "--changelog", "--prerelease", test_input, "--yes")

    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog", "--incremental")

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize(
    "from_pre,to_pre", itertools.product(["alpha", "beta", "rc"], repeat=2)
)
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2021-06-11")
def test_changelog_incremental_with_prerelease_version_to_prerelease_version(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    from_pre: str,
    to_pre: str,
    util: UtilFixture,
):
    with open(changelog_path, "w") as f:
        f.write(KEEP_A_CHANGELOG)
    util.create_file_and_commit("irrelevant commit")
    util.create_tag("1.0.0", annotated=True)

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")

    util.run_cli("bump", "--changelog", "--prerelease", from_pre, "--yes")

    util.run_cli("bump", "--changelog", "--prerelease", to_pre, "--yes")

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2025-12-29")
def test_changelog_release_candidate_version_with_merge_prerelease(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    test_input: str,
    util: UtilFixture,
):
    """Fix #357"""
    with open(changelog_path, "w") as f:
        f.write(KEEP_A_CHANGELOG)
    util.create_file_and_commit("irrelevant commit")
    util.create_tag("1.0.0")

    util.create_file_and_commit("feat: add new output")
    util.create_file_and_commit("fix: output glitch")

    util.run_cli("bump", "--prerelease", test_input, "--yes")

    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog", "--merge-prerelease")

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2023-04-16")
def test_changelog_incremental_with_merge_prerelease(
    changelog_path: str,
    file_regression: FileRegressionFixture,
    test_input: str,
    util: UtilFixture,
):
    """Fix #357"""
    with open(changelog_path, "w") as f:
        f.write(KEEP_A_CHANGELOG)
    util.create_file_and_commit("irrelevant commit")
    util.create_tag("1.0.0")

    util.create_file_and_commit("feat: add new output")

    util.run_cli("bump", "--prerelease", test_input, "--yes", "--changelog")

    util.create_file_and_commit("fix: output glitch")

    util.run_cli("bump", "--prerelease", test_input, "--yes")

    util.create_file_and_commit("fix: mama gotta work")
    util.create_file_and_commit("feat: add more stuff")
    util.create_file_and_commit("Merge into master")

    util.run_cli("changelog", "--merge-prerelease", "--incremental")

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_with_filename_as_empty_string(
    changelog_path: str, config_path: str, util: UtilFixture
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write("changelog_file = true\n")

    util.create_file_and_commit("feat: add new output")

    with pytest.raises(NotAllowed):
        util.run_cli("changelog")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_first_version_from_arg(
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes")

    util.run_cli("changelog", "0.2.0")
    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_latest_version_from_arg(
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes")

    util.run_cli("changelog", "0.3.0")

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "rev_range,tag",
    (
        pytest.param("0.8.0", "0.2.0", id="single-not-found"),
        pytest.param("0.1.0..0.3.0", "0.3.0", id="lower-bound-not-found"),
        pytest.param("0.1.0..0.3.0", "0.1.0", id="upper-bound-not-found"),
        pytest.param("0.3.0..0.4.0", "0.2.0", id="none-found"),
    ),
)
def test_changelog_from_rev_range_not_found(
    config_path: str, rev_range: str, tag: str, util: UtilFixture
):
    """Provides an invalid revision ID to changelog command"""
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.create_tag(tag)
    util.create_file_and_commit("feat: new file")
    util.create_tag("1.0.0")

    with pytest.raises(NoCommitsFoundError) as excinfo:
        util.run_cli("changelog", rev_range)  # it shouldn't exist

    assert "Could not find a valid revision" in str(excinfo)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_multiple_matching_tags(
    config_path: str, changelog_path: str, util: UtilFixture
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "new-$version"\nlegacy_tag_formats = ["legacy-$version"]')

    util.create_file_and_commit("feat: new file")
    util.create_tag("legacy-1.0.0")
    util.create_file_and_commit("feat: new file")
    util.create_tag("legacy-2.0.0")
    util.create_tag("new-2.0.0")

    with pytest.warns() as warnings:
        util.run_cli("changelog", "1.0.0..2.0.0")  # it shouldn't exist

    assert len(warnings) == 1
    warning = warnings[0]
    assert "Multiple tags found for version 2.0.0" in str(warning.message)

    with open(changelog_path) as f:
        out = f.read()

    # Ensure only one tag is rendered
    assert out.count("2.0.0") == 1


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_from_rev_range_default_tag_format(
    config_path: str, changelog_path: str, util: UtilFixture
):
    """Checks that rev_range is calculated with the default (None) tag format"""
    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes")

    util.run_cli("changelog", "0.3.0")

    with open(changelog_path) as f:
        out = f.read()

    assert "new file" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_version_range_including_first_tag(
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes")

    util.run_cli("changelog", "0.2.0..0.3.0")
    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_version_range_from_arg(
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")
    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: getting ready for this")

    util.run_cli("bump", "--yes")

    util.run_cli("changelog", "0.3.0..0.4.0")
    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_version_range_with_legacy_tags(
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    changelog = Path(changelog_path)
    Path(config_path).write_text(
        "\n".join(
            [
                "[tool.commitizen]",
                'version_provider = "scm"',
                'tag_format = "v$version"',
                "legacy_tag_formats = [",
                '  "legacy-${version}",',
                '  "old-${version}",',
                "]",
            ]
        ),
    )

    util.create_file_and_commit("feat: new file")
    util.create_tag("old-0.2.0")
    util.create_file_and_commit("feat: new file")
    util.create_tag("legacy-0.3.0")
    util.create_file_and_commit("feat: new file")
    util.create_tag("legacy-0.4.0")

    util.run_cli("changelog", "0.2.0..0.4.0")
    file_regression.check(changelog.read_text(), extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_version_with_big_range_from_arg(
    config_path, changelog_path, file_regression, util: UtilFixture
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    util.create_file_and_commit("feat: new file")

    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes")  # 0.3.0
    util.create_file_and_commit("feat: getting ready for this")

    util.run_cli("bump", "--yes")  # 0.4.0
    util.create_file_and_commit("fix: small error")

    util.run_cli("bump", "--yes")  # 0.4.1
    util.create_file_and_commit("feat: new shinny feature")

    util.run_cli("bump", "--yes")  # 0.5.0
    util.create_file_and_commit("feat: amazing different shinny feature")

    util.run_cli("bump", "--yes")  # 0.6.0

    util.run_cli("changelog", "0.3.0..0.5.0")
    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_latest_version_dry_run(
    capsys: pytest.CaptureFixture,
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes")
    capsys.readouterr()

    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "0.3.0", "--dry-run")

    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_invalid_subject_is_skipped(capsys: pytest.CaptureFixture, util: UtilFixture):
    """Fix #510"""
    non_conformant_commit_title = (
        "Merge pull request #487 from manang/master\n\n"
        "feat: skip merge messages that start with Pull request\n"
    )
    util.create_file_and_commit(non_conformant_commit_title)
    util.create_file_and_commit("feat: a new world")
    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "--dry-run")
    out, _ = capsys.readouterr()

    assert out == ("## Unreleased\n\n### Feat\n\n- a new world\n\n")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_with_customized_change_type_order(
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a") as f:
        f.write('tag_format = "$version"\n')
        f.write(
            'change_type_order = ["BREAKING CHANGE", "Perf", "Fix", "Feat", "Refactor"]\n'
        )

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")
    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")
    util.create_file_and_commit("fix: fix bug")

    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: getting ready for this")
    util.create_file_and_commit("perf: perf improvement")

    util.run_cli("bump", "--yes")

    util.run_cli("changelog", "0.3.0..0.4.0")
    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_empty_commit_list(mocker: MockFixture, util: UtilFixture):
    util.create_file_and_commit("feat: a new world")

    # test changelog properly handles when no commits are found for the revision
    mocker.patch("commitizen.git.get_commits", return_value=[])
    with pytest.raises(NoCommitsFoundError):
        util.run_cli("changelog")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_prerelease_rev_with_use_scheme_semver(
    mocker: MockFixture,
    capsys: pytest.CaptureFixture,
    config_path: str,
    changelog_path: str,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    with open(config_path, "a") as f:
        f.write('tag_format = "$version"\nversion_scheme = "semver"')

    # create commit and tag
    util.create_file_and_commit("feat: new file")
    util.run_cli("bump", "--yes")

    util.create_file_and_commit("feat: after 0.2.0")
    util.create_file_and_commit("feat: another feature")

    util.run_cli("bump", "--yes", "--prerelease", "alpha")
    capsys.readouterr()

    tag_exists = git.tag_exist("0.3.0-a0")
    assert tag_exists is True

    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "0.3.0-a0", "--dry-run")

    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")

    util.run_cli("bump", "--yes", "--prerelease", "alpha")
    capsys.readouterr()

    tag_exists = git.tag_exist("0.3.0-a1")
    assert tag_exists is True

    with pytest.raises(DryRunExit):
        util.run_cli("changelog", "0.3.0-a1", "--dry-run")

    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".second-prerelease.md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_uses_version_tags_for_header(
    mocker: MockFixture, config: BaseConfig, util: UtilFixture
):
    """Tests that changelog headers always use version tags even if there are non-version tags

    This tests a scenario fixed in this commit:
    The first header was using a non-version tag and outputting "## 0-not-a-version" instead of "## 1.0.0
    """
    util.create_file_and_commit("feat: commit in 1.0.0")
    util.create_tag("0-not-a-version")
    util.create_tag("1.0.0")
    util.create_tag("also-not-a-version")

    write_patch = mocker.patch("commitizen.commands.changelog.out.write")

    changelog = Changelog(
        config, {"dry_run": True, "incremental": True, "unreleased_version": None}
    )

    with pytest.raises(DryRunExit):
        changelog()

    changelog_output = write_patch.call_args[0][0]

    assert changelog_output.startswith("## 1.0.0")
    assert "0-no-a-version" not in changelog_output
    assert "also-not-a-version" not in changelog_output


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_current_version_tag_with_nonversion_tag(
    mocker: MockFixture, config: BaseConfig, util: UtilFixture
):
    """Tests that changelog generation for a single version works even if
    there is a non-version tag in the list of tags

    This tests a scenario which is fixed in this commit:
    You have a commit in between two versions (1.0.0..2.0.0) which is tagged with a non-version tag (not-a-version).
    In this case commitizen should disregard the non-version tag when determining the rev-range & generating the changelog.
    """
    util.create_file_and_commit("feat: initial commit")
    util.create_tag("1.0.0")

    util.create_file_and_commit("feat: commit 1")
    util.create_tag("1-not-a-version")

    util.create_file_and_commit("feat: commit 2")

    util.create_file_and_commit("bump: version 1.0.0 → 2.0.0")
    util.create_tag("2.0.0")

    write_patch = mocker.patch("commitizen.commands.changelog.out.write")

    changelog = Changelog(
        config,
        {
            "dry_run": True,
            "incremental": False,
            "unreleased_version": None,
            "rev_range": "2.0.0",
        },
    )

    with pytest.raises(DryRunExit):
        changelog()

    full_changelog = "\
## 2.0.0 (2022-02-13)\n\n\
### Feat\n\n\
- commit 2\n\
- commit 1\n"

    write_patch.assert_called_with(full_changelog)


@pytest.mark.parametrize(
    "arg,cfg,expected",
    (
        pytest.param("", "", "default", id="default"),
        pytest.param("", "changelog.cfg", "from config", id="from-config"),
        pytest.param(
            "--template=changelog.cmd", "changelog.cfg", "from cmd", id="from-command"
        ),
    ),
)
def test_changelog_template_option_precedence(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    arg: str,
    cfg: str,
    expected: str,
    util: UtilFixture,
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

    testargs = ["changelog"]
    if arg:
        testargs.append(arg)
    util.run_cli(*testargs)

    out = changelog.read_text()
    assert out == expected


def test_changelog_template_extras_precedence(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    mock_plugin: BaseCommitizen,
    any_changelog_format: ChangelogFormat,
    util: UtilFixture,
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

    util.run_cli("changelog", "--extra", "first=from-command")

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == "from-command - from-config - from-plugin"


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2021-06-11")
def test_changelog_only_tag_matching_tag_format_included_prefix(
    mocker: MockFixture,
    changelog_path: Path,
    config_path: Path,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('\ntag_format = "custom${version}"\n')
    util.create_file_and_commit("feat: new file")
    util.create_tag("v0.2.0")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("0.2.0")
    util.create_tag("random0.2.0")
    util.run_cli("bump", "--changelog", "--yes")
    util.create_file_and_commit("feat: another new file")
    util.run_cli("bump", "--changelog", "--yes")
    with open(changelog_path) as f:
        out = f.read()
    assert out.startswith("## custom0.3.0 (2021-06-11)")
    assert "## v0.2.0 (2021-06-11)" not in out
    assert "## 0.2.0  (2021-06-11)" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_only_tag_matching_tag_format_included_prefix_sep(
    mocker: MockFixture,
    changelog_path: Path,
    config_path: Path,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('\ntag_format = "custom-${version}"\n')
    util.create_file_and_commit("feat: new file")
    util.create_tag("v0.2.0")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("0.2.0")
    util.create_tag("random0.2.0")
    util.run_cli("bump", "--changelog", "--yes")
    with open(changelog_path) as f:
        out = f.read()
    util.create_file_and_commit("feat: new version another new file")
    util.create_file_and_commit("feat: new version some new file")
    util.run_cli("bump", "--changelog")
    with open(changelog_path) as f:
        out = f.read()
    assert out.startswith("## custom-0.3.0")
    assert "## v0.2.0" not in out
    assert "## 0.2.0" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2021-06-11")
def test_changelog_only_tag_matching_tag_format_included_suffix(
    changelog_path: Path,
    config_path: Path,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('\ntag_format = "${version}custom"\n')
    util.create_file_and_commit("feat: new file")
    util.create_tag("v0.2.0")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("0.2.0")
    util.create_tag("random0.2.0")
    # bump to 0.2.0custom
    util.run_cli("bump", "--changelog", "--yes")

    util.create_file_and_commit("feat: another new file")
    # bump to 0.3.0custom
    util.run_cli("bump", "--changelog", "--yes")
    with open(changelog_path) as f:
        out = f.read()
    assert out.startswith("## 0.3.0custom (2021-06-11)")
    assert "## v0.2.0 (2021-06-11)" not in out
    assert "## 0.2.0  (2021-06-11)" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2021-06-11")
def test_changelog_only_tag_matching_tag_format_included_suffix_sep(
    changelog_path: Path,
    config_path: Path,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('\ntag_format = "${version}-custom"\n')
    util.create_file_and_commit("feat: new file")
    util.create_tag("v0.2.0")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("0.2.0")
    util.create_tag("random0.2.0")
    util.run_cli("bump", "--changelog", "--yes")
    util.create_file_and_commit("feat: another new file")
    util.run_cli("bump", "--changelog", "--yes")
    with open(changelog_path) as f:
        out = f.read()
    assert out.startswith("## 0.3.0-custom (2021-06-11)")
    assert "## v0.2.0 (2021-06-11)" not in out
    assert "## 0.2.0  (2021-06-11)" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_legacy_tags(
    mocker: MockFixture,
    changelog_path: Path,
    config_path: Path,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.writelines(
            [
                'tag_format = "v${version}"\n',
                "legacy_tag_formats = [\n",
                '  "older-${version}",\n',
                '  "oldest-${version}",\n',
                "]\n",
            ]
        )
    util.create_file_and_commit("feat: new file")
    util.create_tag("oldest-0.1.0")
    util.create_file_and_commit("feat: new file")
    util.create_tag("older-0.2.0")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("v0.3.0")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("not-0.3.1")
    util.run_cli("bump", "--changelog", "--yes")
    out = open(changelog_path).read()
    assert "## v0.3.0" in out
    assert "## older-0.2.0" in out
    assert "## oldest-0.1.0" in out
    assert "## v0.3.0" in out
    assert "## not-0.3.1" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2024-11-18")
def test_changelog_incremental_change_tag_format(
    mocker: MockFixture,
    changelog_path: Path,
    config_path: Path,
    file_regression: FileRegressionFixture,
    util: UtilFixture,
):
    util.freezer.move_to("2024-11-18")
    config = Path(config_path)
    base_config = config.read_text()
    config.write_text(
        "\n".join(
            (
                base_config,
                'tag_format = "older-${version}"',
            )
        )
    )
    util.create_file_and_commit("feat: new file")
    util.create_tag("older-0.1.0")
    util.create_file_and_commit("feat: new file")
    util.create_tag("older-0.2.0")
    util.run_cli("changelog")

    config.write_text(
        "\n".join(
            (
                base_config,
                'tag_format = "v${version}"',
                'legacy_tag_formats = ["older-${version}"]',
            )
        )
    )
    util.create_file_and_commit("feat: another new file")
    util.create_tag("v0.3.0")
    util.run_cli("changelog", "--incremental")
    out = open(changelog_path).read()
    assert "## v0.3.0" in out
    assert "## older-0.2.0" in out
    assert "## older-0.1.0" in out
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_ignored_tags(
    mocker: MockFixture,
    changelog_path: Path,
    config_path: Path,
    capsys: pytest.CaptureFixture,
    util: UtilFixture,
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.writelines(
            [
                'tag_format = "v${version}"\n',
                "ignored_tag_formats = [\n",
                '  "ignored",\n',
                '  "ignore-${version}",\n',
                "]\n",
            ]
        )
    util.create_file_and_commit("feat: new file")
    util.create_tag("ignore-0.1.0")
    util.create_file_and_commit("feat: new file")
    util.create_tag("ignored")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("v0.3.0")
    util.create_file_and_commit("feat: another new file")
    util.create_tag("not-ignored")
    util.run_cli("bump", "--changelog", "--yes")
    out = open(changelog_path).read()
    _, err = capsys.readouterr()
    assert "## ignore-0.1.0" not in out
    assert "Invalid version tag: 'ignore-0.1.0'" not in err
    assert "## ignored" not in out
    assert "Invalid version tag: 'ignored'" not in err
    assert "## not-ignored" not in out
    assert "Invalid version tag: 'not-ignored'" in err
    assert "## v0.3.0" in out
    assert "Invalid version tag: 'v0.3.0'" not in err


def test_changelog_template_extra_quotes(
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    util: UtilFixture,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("{{first}} - {{second}} - {{third}}")

    util.create_file_and_commit("feat: new file")

    util.run_cli(
        "changelog",
        "-e",
        "first=no-quote",
        "-e",
        "second='single quotes'",
        "-e",
        'third="double quotes"',
    )

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == "no-quote - single quotes - double quotes"


@pytest.mark.parametrize(
    "extra, expected",
    (
        pytest.param("key=value=", "value=", id="2-equals"),
        pytest.param("key==value", "=value", id="2-consecutives-equals"),
        pytest.param("key==value==", "=value==", id="multiple-equals"),
    ),
)
def test_changelog_template_extra_weird_but_valid(
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    extra: str,
    expected: str,
    util: UtilFixture,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("{{key}}")

    util.create_file_and_commit("feat: new file")

    util.run_cli("changelog", "-e", extra)

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == expected


@pytest.mark.parametrize("extra", ("no-equal", "", "=no-key"))
def test_changelog_template_extra_bad_format(
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    extra: str,
    util: UtilFixture,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("")

    util.create_file_and_commit("feat: new file")

    with pytest.raises(InvalidCommandArgumentError):
        util.run_cli("changelog", "-e", extra)


def test_export_changelog_template_from_default(
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    util: UtilFixture,
    repo_root: Path,
):
    project_root = Path(tmp_commitizen_project)
    target = project_root / "changelog.jinja"
    src = repo_root / "commitizen" / "templates" / any_changelog_format.template

    util.run_cli("changelog", "--export-template", str(target))

    assert target.exists()
    assert target.read_text() == src.read_text()


def test_export_changelog_template_from_plugin(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    mock_plugin: BaseCommitizen,
    changelog_format: ChangelogFormat,
    tmp_path: Path,
    util: UtilFixture,
):
    project_root = Path(tmp_commitizen_project)
    target = project_root / "changelog.jinja"
    src = tmp_path / changelog_format.template
    tpl = "I am a custom template"
    src.write_text(tpl)
    mock_plugin.template_loader = FileSystemLoader(tmp_path)

    util.run_cli("changelog", "--export-template", str(target))

    assert target.exists()
    assert target.read_text() == tpl


def test_export_changelog_template_fails_when_template_has_no_filename(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    util: UtilFixture,
):
    project_root = Path(tmp_commitizen_project)
    target = project_root / "changelog.jinja"

    # Mock a template object with no filename
    class FakeTemplate:
        filename = None

    # Patch get_changelog_template to return a template without a filename
    mocker.patch(
        "commitizen.changelog.get_changelog_template", return_value=FakeTemplate()
    )

    with pytest.raises(NotAllowed) as exc_info:
        util.run_cli("changelog", "--export-template", str(target))

    assert not target.exists()
    assert "Template filename is not set" in str(exc_info.value)


def test_changelog_template_incremental_variable(
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    util: UtilFixture,
    file_regression: FileRegressionFixture,
):
    """
    Test that the changelog template is not rendered when the incremental flag is not set.
    Reference: https://github.com/commitizen-tools/commitizen/discussions/1620
    """
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text(
        dedent("""
        {% if not incremental %}
        # CHANGELOG
        {% endif %}

        {% for entry in tree %}

        ## {{ entry.version }}{% if entry.date %} ({{ entry.date }}){% endif %}

        {% for change_key, changes in entry.changes.items() %}

        {% if change_key %}
        ### {{ change_key }}
        {% endif %}

        {% for change in changes %}
        {% if change.scope %}
        - **{{ change.scope }}**: {{ change.message }}
        {% elif change.message %}
        - {{ change.message }}
        {% endif %}
        {% endfor %}
        {% endfor %}
        {% endfor %}
        """)
    )
    target = "CHANGELOG.md"

    util.create_file_and_commit("feat(foo): new file")
    util.run_cli("changelog", "--file-name", target)
    with open(target, encoding="utf-8") as f:
        out = f.read()
    file_regression.check(out, extension=".md")

    util.create_file_and_commit("refactor(bar): another new file")
    util.run_cli("changelog", "--file-name", target, "--incremental")
    with open(target, encoding="utf-8") as f:
        out = f.read()
    file_regression.check(out, extension=".incremental.md")
