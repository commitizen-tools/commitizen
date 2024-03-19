import itertools
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest
from dateutil import relativedelta
from jinja2 import FileSystemLoader
from pytest_mock import MockFixture

from commitizen import __file__ as commitizen_init
from commitizen import cli, git
from commitizen.commands.changelog import Changelog
from commitizen.config.base_config import BaseConfig
from commitizen.cz.base import BaseCommitizen
from commitizen.exceptions import (
    DryRunExit,
    InvalidCommandArgumentError,
    NoCommitsFoundError,
    NoRevisionError,
    NotAGitProjectError,
    NotAllowed,
)
from commitizen.changelog_formats import ChangelogFormat
from tests.utils import (
    create_branch,
    create_file_and_commit,
    create_tag,
    get_current_branch,
    merge_branch,
    switch_branch,
    wait_for_tag,
)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_from_version_zero_point_two(
    mocker: MockFixture, capsys, file_regression
):
    create_file_and_commit("feat: new file")
    create_file_and_commit("refactor: not in changelog")

    # create tag
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    capsys.readouterr()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: after 0.2")

    testargs = ["cz", "changelog", "--start-rev", "0.2.0", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_with_different_cz(mocker: MockFixture, capsys, file_regression):
    create_file_and_commit("JRA-34 #comment corrected indent issue")
    create_file_and_commit("JRA-35 #time 1w 2d 4h 30m Total work logged")

    testargs = ["cz", "-n", "cz_jira", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_from_start(
    mocker: MockFixture, capsys, changelog_format: ChangelogFormat, file_regression
):
    create_file_and_commit("feat: new file")
    create_file_and_commit("refactor: is in changelog")
    create_file_and_commit("Merge into master")
    changelog_file = f"CHANGELOG.{changelog_format.extension}"
    template = f"CHANGELOG.{changelog_format.extension}.j2"

    testargs = [
        "cz",
        "changelog",
        "--file-name",
        changelog_file,
        "--template",
        template,
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_file, encoding="utf-8") as f:
        out = f.read()
    file_regression.check(out, extension=changelog_format.ext)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_replacing_unreleased_using_incremental(
    mocker: MockFixture, capsys, changelog_format: ChangelogFormat, file_regression
):
    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")
    create_file_and_commit("Merge into master")
    changelog_file = f"CHANGELOG.{changelog_format.extension}"
    template = f"CHANGELOG.{changelog_format.extension}.j2"

    testargs = [
        "cz",
        "changelog",
        "--file-name",
        changelog_file,
        "--template",
        template,
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    testargs = [
        "cz",
        "bump",
        "--yes",
        "--file-name",
        changelog_file,
        "--template",
        template,
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = [
        "cz",
        "changelog",
        "--incremental",
        "--file-name",
        changelog_file,
        "--template",
        template,
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_file, encoding="utf-8") as f:
        out = f.read().replace(
            datetime.strftime(datetime.now(), "%Y-%m-%d"), "2022-08-14"
        )

    file_regression.check(out, extension=changelog_format.ext)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_is_persisted_using_incremental(
    mocker: MockFixture, capsys, changelog_path, file_regression
):
    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    testargs = ["cz", "changelog"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, "a", encoding="utf-8") as f:
        f.write("\nnote: this should be persisted using increment\n")

    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--incremental"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read().replace(
            datetime.strftime(datetime.now(), "%Y-%m-%d"), "2022-08-14"
        )

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_angular_sample(
    mocker: MockFixture, capsys, changelog_path, file_regression
):
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(
            "# [10.0.0-rc.3](https://github.com/angular/angular/compare/10.0.0-rc.2...10.0.0-rc.3) (2020-04-22)\n"
            "\n"
            "### Bug Fixes"
            "\n"
            "* **common:** format day-periods that cross midnight ([#36611](https://github.com/angular/angular/issues/36611)) ([c6e5fc4](https://github.com/angular/angular/commit/c6e5fc4)), closes [#36566](https://github.com/angular/angular/issues/36566)\n"
        )
    create_file_and_commit("irrelevant commit")
    git.tag("10.0.0-rc.3")

    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")
    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--incremental"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

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
    mocker: MockFixture, capsys, changelog_path, file_regression
):
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(KEEP_A_CHANGELOG)
    create_file_and_commit("irrelevant commit")
    git.tag("1.0.0")

    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")
    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--incremental"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize("dry_run", [True, False])
def test_changelog_hook(mocker: MockFixture, config: BaseConfig, dry_run: bool):
    changelog_hook_mock = mocker.Mock()
    changelog_hook_mock.return_value = "cool changelog hook"

    create_file_and_commit("feat: new file")
    create_file_and_commit("refactor: is in changelog")
    create_file_and_commit("Merge into master")

    config.settings["change_type_order"] = ["Refactor", "Feat"]  # type: ignore[typeddict-unknown-key]
    changelog = Changelog(
        config, {"unreleased_version": None, "incremental": True, "dry_run": dry_run}
    )
    mocker.patch.object(changelog.cz, "changelog_hook", changelog_hook_mock)
    try:
        changelog()
    except DryRunExit:
        pass

    full_changelog = (
        "## Unreleased\n\n### Refactor\n\n- is in changelog\n\n### Feat\n\n- new file\n"
    )
    partial_changelog = full_changelog
    if dry_run:
        partial_changelog = ""

    changelog_hook_mock.assert_called_with(full_changelog, partial_changelog)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_hook_customize(mocker: MockFixture, config_customize):
    changelog_hook_mock = mocker.Mock()
    changelog_hook_mock.return_value = "cool changelog hook"

    create_file_and_commit("feat: new file")
    create_file_and_commit("refactor: is in changelog")
    create_file_and_commit("Merge into master")

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
def test_changelog_release_hook(mocker: MockFixture, config):
    def changelog_release_hook(release: dict, tag: git.GitTag) -> dict:
        return release

    for i in range(3):
        create_file_and_commit("feat: new file")
        create_file_and_commit("refactor: is in changelog")
        create_file_and_commit("Merge into master")
        git.tag(f"0.{i + 1}.0")

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
    mocker: MockFixture, config_customize
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

    create_file_and_commit("feat: initial commit")

    main_branch = get_current_branch()

    create_branch("branchA")
    create_branch("branchB")

    switch_branch("branchA")
    create_file_and_commit("feat: I will be merged second")

    switch_branch("branchB")
    create_file_and_commit("feat: I will be merged first")

    # Note we merge branches opposite order than author_date
    switch_branch(main_branch)
    merge_branch("branchB")
    merge_branch("branchA")

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
    mocker: MockFixture, capsys, changelog_path, file_regression
):
    """Test for bug https://github.com/commitizen-tools/commitizen/issues/192"""
    create_file_and_commit("feat: add new output")

    testargs = ["cz", "changelog", "--incremental"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: output glitch")

    testargs = ["cz", "changelog", "--incremental"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: no more explosions")

    testargs = ["cz", "changelog", "--incremental"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("feat: add more stuff")

    testargs = ["cz", "changelog", "--incremental"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_newline_separates_new_content_from_old(
    mocker: MockFixture, changelog_path
):
    """Test for https://github.com/commitizen-tools/commitizen/issues/509"""
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("Pre-existing content that should be kept\n")

    create_file_and_commit("feat: add more cat videos")

    testargs = ["cz", "changelog", "--incremental"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    assert (
        out
        == "Pre-existing content that should be kept\n\n## Unreleased\n\n### Feat\n\n- add more cat videos\n"
    )


def test_changelog_without_revision(mocker: MockFixture, tmp_commitizen_project):
    changelog_file = tmp_commitizen_project.join("CHANGELOG.md")
    changelog_file.write(
        """
        # Unreleased

        ## v1.0.0
        """
    )

    # create_file_and_commit("feat: new file")
    testargs = ["cz", "changelog", "--incremental"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoRevisionError):
        cli.main()


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_with_revision(mocker):
    """combining incremental with a revision doesn't make sense"""
    testargs = ["cz", "changelog", "--incremental", "0.2.0"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NotAllowed):
        cli.main()


def test_changelog_with_different_tag_name_and_changelog_content(
    mocker: MockFixture, tmp_commitizen_project
):
    changelog_file = tmp_commitizen_project.join("CHANGELOG.md")
    changelog_file.write(
        """
        # Unreleased

        ## v1.0.0
        """
    )
    create_file_and_commit("feat: new file")
    git.tag("2.0.0")

    # create_file_and_commit("feat: new file")
    testargs = ["cz", "changelog", "--incremental"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoRevisionError):
        cli.main()


def test_changelog_in_non_git_project(tmpdir, config, mocker: MockFixture):
    testargs = ["cz", "changelog", "--incremental"]
    mocker.patch.object(sys, "argv", testargs)

    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            cli.main()


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_beta(mocker: MockFixture, capsys, file_regression):
    commit_message = (
        "feat(users): email pattern corrected\n\n"
        "BREAKING CHANGE: migrate by renaming user to users\n\n"
        "footer content"
    )
    create_file_and_commit(commit_message)
    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1(mocker: MockFixture, capsys, file_regression):
    commit_message = (
        "feat(users): email pattern corrected\n\n"
        "body content\n\n"
        "BREAKING CHANGE: migrate by renaming user to users"
    )
    create_file_and_commit(commit_message)
    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_multiline(
    mocker: MockFixture, capsys, file_regression
):
    commit_message = (
        "feat(users): email pattern corrected\n\n"
        "body content\n\n"
        "BREAKING CHANGE: migrate by renaming user to users.\n"
        "and then connect the thingy with the other thingy\n\n"
        "footer content"
    )
    create_file_and_commit(commit_message)
    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_with_exclamation_mark(
    mocker: MockFixture, capsys, file_regression
):
    commit_message = "chore!: drop support for py36"
    create_file_and_commit(commit_message)
    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_breaking_change_content_v1_with_exclamation_mark_feat(
    mocker: MockFixture, capsys, file_regression
):
    commit_message = "feat(pipeline)!: some text with breaking change"
    create_file_and_commit(commit_message)
    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_config_flag_increment(
    mocker: MockFixture, changelog_path, config_path, file_regression
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write("changelog_incremental = true\n")
    with open(changelog_path, "a", encoding="utf-8") as f:
        f.write("\nnote: this should be persisted using increment\n")

    create_file_and_commit("feat: add new output")

    testargs = ["cz", "changelog"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    assert "this should be persisted using increment" in out
    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_config_flag_merge_prerelease(
    mocker: MockFixture, changelog_path, config_path, file_regression, test_input
):
    with open(config_path, "a") as f:
        f.write("changelog_merge_prerelease = true\n")

    create_file_and_commit("irrelevant commit")
    mocker.patch("commitizen.git.GitTag.date", "1970-01-01")
    git.tag("1.0.0")

    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")

    testargs = ["cz", "bump", "--prerelease", test_input, "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_config_start_rev_option(
    mocker: MockFixture, capsys, config_path, file_regression
):
    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    capsys.readouterr()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: after 0.2")

    with open(config_path, "a", encoding="utf-8") as f:
        f.write('changelog_start_rev = "0.2.0"\n')

    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_incremental_keep_a_changelog_sample_with_annotated_tag(
    mocker: MockFixture, capsys, changelog_path, file_regression
):
    """Fix #378"""
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(KEEP_A_CHANGELOG)
    create_file_and_commit("irrelevant commit")
    git.tag("1.0.0", annotated=True)

    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")
    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--incremental"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2021-06-11")
def test_changelog_incremental_with_release_candidate_version(
    mocker: MockFixture, changelog_path, file_regression, test_input
):
    """Fix #357"""
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(KEEP_A_CHANGELOG)
    create_file_and_commit("irrelevant commit")
    git.tag("1.0.0", annotated=True)

    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")

    testargs = ["cz", "bump", "--changelog", "--prerelease", test_input, "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--incremental"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize(
    "from_pre,to_pre", itertools.product(["alpha", "beta", "rc"], repeat=2)
)
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2021-06-11")
def test_changelog_incremental_with_prerelease_version_to_prerelease_version(
    mocker: MockFixture, changelog_path, file_regression, from_pre, to_pre
):
    with open(changelog_path, "w") as f:
        f.write(KEEP_A_CHANGELOG)
    create_file_and_commit("irrelevant commit")
    git.tag("1.0.0", annotated=True)

    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")

    testargs = ["cz", "bump", "--changelog", "--prerelease", from_pre, "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    testargs = ["cz", "bump", "--changelog", "--prerelease", to_pre, "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_release_candidate_version_with_merge_prerelease(
    mocker: MockFixture, changelog_path, file_regression, test_input
):
    """Fix #357"""
    with open(changelog_path, "w") as f:
        f.write(KEEP_A_CHANGELOG)
    create_file_and_commit("irrelevant commit")
    mocker.patch("commitizen.git.GitTag.date", "1970-01-01")
    git.tag("1.0.0")

    create_file_and_commit("feat: add new output")
    create_file_and_commit("fix: output glitch")

    testargs = ["cz", "bump", "--prerelease", test_input, "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--merge-prerelease"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.parametrize("test_input", ["rc", "alpha", "beta"])
@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2023-04-16")
def test_changelog_incremental_with_merge_prerelease(
    mocker: MockFixture, changelog_path, file_regression, test_input
):
    """Fix #357"""
    with open(changelog_path, "w") as f:
        f.write(KEEP_A_CHANGELOG)
    create_file_and_commit("irrelevant commit")
    mocker.patch("commitizen.git.GitTag.date", "1970-01-01")
    git.tag("1.0.0")

    create_file_and_commit("feat: add new output")

    testargs = ["cz", "bump", "--prerelease", test_input, "--yes", "--changelog"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: output glitch")

    testargs = ["cz", "bump", "--prerelease", test_input, "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("fix: mama gotta work")
    create_file_and_commit("feat: add more stuff")
    create_file_and_commit("Merge into master")

    testargs = ["cz", "changelog", "--merge-prerelease", "--incremental"]

    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_with_filename_as_empty_string(
    mocker: MockFixture, changelog_path, config_path
):
    with open(config_path, "a", encoding="utf-8") as f:
        f.write("changelog_file = true\n")

    create_file_and_commit("feat: add new output")

    testargs = ["cz", "changelog"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(NotAllowed):
        cli.main()


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_first_version_from_arg(
    mocker: MockFixture, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    testargs = ["cz", "changelog", "0.2.0"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_latest_version_from_arg(
    mocker: MockFixture, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    wait_for_tag()

    testargs = ["cz", "changelog", "0.3.0"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_single_version_not_found(
    mocker: MockFixture, config_path, changelog_path
):
    """Provides an invalid revision ID to changelog command"""
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    wait_for_tag()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    testargs = ["cz", "changelog", "0.8.0"]  # it shouldn't exist
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(NoCommitsFoundError) as excinfo:
        cli.main()

    assert "Could not find a valid revision" in str(excinfo)


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_range_default_tag_format(
    mocker, config_path, changelog_path
):
    """Checks that rev_range is calculated with the default (None) tag format"""
    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    testargs = ["cz", "changelog", "0.3.0"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    with open(changelog_path) as f:
        out = f.read()

    assert "new file" not in out


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_range_version_not_found(mocker: MockFixture, config_path):
    """Provides an invalid end revision ID to changelog command"""
    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    testargs = ["cz", "changelog", "0.5.0..0.8.0"]  # it shouldn't exist
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(NoCommitsFoundError) as excinfo:
        cli.main()

    assert "Could not find a valid revision" in str(excinfo)


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_version_range_including_first_tag(
    mocker: MockFixture, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    testargs = ["cz", "changelog", "0.2.0..0.3.0"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    with open(changelog_path, encoding="utf-8") as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_version_range_from_arg(
    mocker: MockFixture, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()
    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: getting ready for this")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    testargs = ["cz", "changelog", "0.3.0..0.4.0"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_version_with_big_range_from_arg(
    mocker: MockFixture, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a", encoding="utf-8") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]  # 0.3.0
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()
    create_file_and_commit("feat: getting ready for this")

    testargs = ["cz", "bump", "--yes"]  # 0.4.0
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()
    create_file_and_commit("fix: small error")

    testargs = ["cz", "bump", "--yes"]  # 0.4.1
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()
    create_file_and_commit("feat: new shinny feature")

    testargs = ["cz", "bump", "--yes"]  # 0.5.0
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()
    create_file_and_commit("feat: amazing different shinny feature")
    # dirty hack to avoid same time between tags

    testargs = ["cz", "bump", "--yes"]  # 0.6.0
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    testargs = ["cz", "changelog", "0.3.0..0.5.0"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_from_rev_latest_version_dry_run(
    mocker: MockFixture, capsys, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a") as f:
        f.write('tag_format = "$version"\n')

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    capsys.readouterr()
    wait_for_tag()

    testargs = ["cz", "changelog", "0.3.0", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()

    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_invalid_subject_is_skipped(mocker: MockFixture, capsys):
    """Fix #510"""
    non_conformant_commit_title = (
        "Merge pull request #487 from manang/master\n\n"
        "feat: skip merge messages that start with Pull request\n"
    )
    create_file_and_commit(non_conformant_commit_title)
    create_file_and_commit("feat: a new world")
    testargs = ["cz", "changelog", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()
    out, _ = capsys.readouterr()

    assert out == ("## Unreleased\n\n### Feat\n\n- a new world\n\n")


@pytest.mark.freeze_time("2022-02-13")
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_with_customized_change_type_order(
    mocker, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a") as f:
        f.write('tag_format = "$version"\n')
        f.write(
            'change_type_order = ["BREAKING CHANGE", "Perf", "Fix", "Feat", "Refactor"]\n'
        )

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()
    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")
    create_file_and_commit("fix: fix bug")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: getting ready for this")
    create_file_and_commit("perf: perf improvement")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    testargs = ["cz", "changelog", "0.3.0..0.4.0"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    with open(changelog_path) as f:
        out = f.read()

    file_regression.check(out, extension=".md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_empty_commit_list(mocker):
    create_file_and_commit("feat: a new world")

    # test changelog properly handles when no commits are found for the revision
    mocker.patch("commitizen.git.get_commits", return_value=[])
    testargs = ["cz", "changelog"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(NoCommitsFoundError):
        cli.main()


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.freeze_time("2022-02-13")
def test_changelog_prerelease_rev_with_use_scheme_semver(
    mocker: MockFixture, capsys, config_path, changelog_path, file_regression
):
    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")

    with open(config_path, "a") as f:
        f.write('tag_format = "$version"\n' 'version_scheme = "semver"')

    # create commit and tag
    create_file_and_commit("feat: new file")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    wait_for_tag()

    create_file_and_commit("feat: after 0.2.0")
    create_file_and_commit("feat: another feature")

    testargs = ["cz", "bump", "--yes", "--prerelease", "alpha"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    capsys.readouterr()
    wait_for_tag()

    tag_exists = git.tag_exist("0.3.0-a0")
    assert tag_exists is True

    testargs = ["cz", "changelog", "0.3.0-a0", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()

    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".md")

    testargs = ["cz", "bump", "--yes", "--prerelease", "alpha"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    capsys.readouterr()
    wait_for_tag()

    tag_exists = git.tag_exist("0.3.0-a1")
    assert tag_exists is True

    testargs = ["cz", "changelog", "0.3.0-a1", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()

    out, _ = capsys.readouterr()

    file_regression.check(out, extension=".second-prerelease.md")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_changelog_uses_version_tags_for_header(mocker: MockFixture, config):
    """Tests that changelog headers always use version tags even if there are non-version tags

    This tests a scenario fixed in this commit:
    The first header was using a non-version tag and outputting "## 0-not-a-version" instead of "## 1.0.0
    """
    create_file_and_commit("feat: commit in 1.0.0")
    create_tag("0-not-a-version")
    create_tag("1.0.0")
    create_tag("also-not-a-version")

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
def test_changelog_from_current_version_tag_with_nonversion_tag(
    mocker: MockFixture, config
):
    """Tests that changelog generation for a single version works even if
    there is a non-version tag in the list of tags

    This tests a scenario which is fixed in this commit:
    You have a commit in between two versions (1.0.0..2.0.0) which is tagged with a non-version tag (not-a-version).
    In this case commitizen should disregard the non-version tag when determining the rev-range & generating the changelog.
    """
    create_file_and_commit(
        "feat: initial commit",
        committer_date=(
            datetime.now() - relativedelta.relativedelta(seconds=3)
        ).isoformat(),
    )
    create_tag("1.0.0")

    create_file_and_commit(
        "feat: commit 1",
        committer_date=(
            datetime.now() - relativedelta.relativedelta(seconds=2)
        ).isoformat(),
    )
    create_tag("1-not-a-version")

    create_file_and_commit(
        "feat: commit 2",
        committer_date=(
            datetime.now() - relativedelta.relativedelta(seconds=1)
        ).isoformat(),
    )

    create_file_and_commit("bump: version 1.0.0 → 2.0.0")
    create_tag("2.0.0")

    mocker.patch("commitizen.git.GitTag.date", "2022-02-13")
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
def test_changelog_template_option_precedance(
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

    testargs = ["cz", "changelog"]
    if arg:
        testargs.append(arg)
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    out = changelog.read_text()
    assert out == expected


def test_changelog_template_extras_precedance(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    mock_plugin: BaseCommitizen,
    any_changelog_format: ChangelogFormat,
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

    testargs = ["cz", "changelog", "--extra", "first=from-command"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == "from-command - from-config - from-plugin"


def test_changelog_template_extra_quotes(
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
        "changelog",
        "-e",
        "first=no-quote",
        "-e",
        "second='single quotes'",
        "-e",
        'third="double quotes"',
    ]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

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
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    extra: str,
    expected,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("{{key}}")

    create_file_and_commit("feat: new file")

    testargs = ["cz", "changelog", "-e", extra]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    changelog = project_root / any_changelog_format.default_changelog_file
    assert changelog.read_text() == expected


@pytest.mark.parametrize("extra", ("no-equal", "", "=no-key"))
def test_changelog_template_extra_bad_format(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
    extra: str,
):
    project_root = Path(tmp_commitizen_project)
    changelog_tpl = project_root / any_changelog_format.template
    changelog_tpl.write_text("")

    create_file_and_commit("feat: new file")

    testargs = ["cz", "changelog", "-e", extra]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(InvalidCommandArgumentError):
        cli.main()


def test_export_changelog_template_from_default(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    any_changelog_format: ChangelogFormat,
):
    project_root = Path(tmp_commitizen_project)
    target = project_root / "changelog.jinja"
    src = Path(commitizen_init).parent / "templates" / any_changelog_format.template

    args = ["cz", "changelog", "--export-template", str(target)]

    mocker.patch.object(sys, "argv", args)
    cli.main()

    assert target.exists()
    assert target.read_text() == src.read_text()


def test_export_changelog_template_from_plugin(
    mocker: MockFixture,
    tmp_commitizen_project: Path,
    mock_plugin: BaseCommitizen,
    changelog_format: ChangelogFormat,
    tmp_path: Path,
):
    project_root = Path(tmp_commitizen_project)
    target = project_root / "changelog.jinja"
    src = tmp_path / changelog_format.template
    tpl = "I am a custom template"
    src.write_text(tpl)
    mock_plugin.template_loader = FileSystemLoader(tmp_path)

    args = ["cz", "changelog", "--export-template", str(target)]

    mocker.patch.object(sys, "argv", args)
    cli.main()

    assert target.exists()
    assert target.read_text() == tpl
