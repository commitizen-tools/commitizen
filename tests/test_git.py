from __future__ import annotations

import inspect
import os
import platform
import shutil

import pytest
from commitizen import cmd, exceptions, git
from pytest_mock import MockFixture

from tests.utils import (
    FakeCommand,
    create_file_and_commit,
    create_tag,
    create_branch,
    switch_branch,
)


def test_git_object_eq():
    git_commit = git.GitCommit(
        rev="sha1-code", title="this is title", body="this is body"
    )
    git_tag = git.GitTag(rev="sha1-code", name="0.0.1", date="2020-01-21")

    assert git_commit == git_tag
    assert git_commit != "sha1-code"


def test_get_tags(mocker: MockFixture):
    tag_str = (
        "v1.0.0---inner_delimiter---333---inner_delimiter---2020-01-20---inner_delimiter---\n"
        "v0.5.0---inner_delimiter---222---inner_delimiter---2020-01-17---inner_delimiter---\n"
        "v0.0.1---inner_delimiter---111---inner_delimiter---2020-01-17---inner_delimiter---\n"
    )
    mocker.patch("commitizen.cmd.run", return_value=FakeCommand(out=tag_str))

    git_tags = git.get_tags()
    latest_git_tag = git_tags[0]
    assert latest_git_tag.rev == "333"
    assert latest_git_tag.name == "v1.0.0"
    assert latest_git_tag.date == "2020-01-20"

    mocker.patch(
        "commitizen.cmd.run", return_value=FakeCommand(out="", err="No tag available")
    )
    assert git.get_tags() == []


def test_get_reachable_tags(tmp_commitizen_project):
    with tmp_commitizen_project.as_cwd():
        create_file_and_commit("Initial state")
        create_tag("1.0.0")
        # create develop
        create_branch("develop")
        switch_branch("develop")

        # add a feature to develop
        create_file_and_commit("develop")
        create_tag("1.1.0b0")

        # create staging
        switch_branch("master")
        create_file_and_commit("master")
        create_tag("1.0.1")

        tags = git.get_tags(reachable_only=True)
        tag_names = set([t.name for t in tags])
        # 1.1.0b0 is not present
        assert tag_names == {"1.0.0", "1.0.1"}


def test_get_tag_names(mocker: MockFixture):
    tag_str = "v1.0.0\n" "v0.5.0\n" "v0.0.1\n"
    mocker.patch("commitizen.cmd.run", return_value=FakeCommand(out=tag_str))

    assert git.get_tag_names() == ["v1.0.0", "v0.5.0", "v0.0.1"]

    mocker.patch(
        "commitizen.cmd.run", return_value=FakeCommand(out="", err="No tag available")
    )
    assert git.get_tag_names() == []


def test_git_message_with_empty_body():
    commit_title = "Some Title"
    commit = git.GitCommit("test_rev", "Some Title", body="")

    assert commit.message == commit_title


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_get_log_as_str_list_empty():
    """ensure an exception or empty list in an empty project"""
    try:
        gitlog = git._get_log_as_str_list(start=None, end="HEAD", args="")
    except exceptions.GitCommandError:
        return
    assert len(gitlog) == 0, "list should be empty if no assert"


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_get_commits():
    create_file_and_commit("feat(users): add username")
    create_file_and_commit("fix: username exception")
    commits = git.get_commits()
    assert len(commits) == 2


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_get_commits_author_and_email():
    create_file_and_commit("fix: username exception")
    commit = git.get_commits()[0]

    assert commit.author != ""
    assert "@" in commit.author_email


def test_get_commits_without_email(mocker: MockFixture):
    raw_commit = (
        "a515bb8f71c403f6f7d1c17b9d8ebf2ce3959395\n"
        "\n"
        "user name\n"
        "\n"
        "----------commit-delimiter----------\n"
        "12d3b4bdaa996ea7067a07660bb5df4772297bdd\n"
        "feat(users): add username\n"
        "user name\n"
        "\n"
        "----------commit-delimiter----------\n"
    )
    mocker.patch("commitizen.cmd.run", return_value=FakeCommand(out=raw_commit))

    commits = git.get_commits()

    assert commits[0].author == "user name"
    assert commits[1].author == "user name"

    assert commits[0].author_email == ""
    assert commits[1].author_email == ""

    assert commits[0].title == ""
    assert commits[1].title == "feat(users): add username"


def test_get_commits_without_breakline_in_each_commit(mocker: MockFixture):
    raw_commit = (
        "ae9ba6fc5526cf478f52ef901418d85505109744\n"
        "bump: version 2.13.0 → 2.14.0\n"
        "GitHub Action\n"
        "action@github.com\n"
        "----------commit-delimiter----------\n"
        "ff2f56ca844de72a9d59590831087bf5a97bac84\n"
        "Merge pull request #332 from cliles/feature/271-redux\n"
        "User\n"
        "user@email.com\n"
        "Feature/271 redux----------commit-delimiter----------\n"
        "20a54bf1b82cd7b573351db4d1e8814dd0be205d\n"
        "feat(#271): enable creation of annotated tags when bumping\n"
        "User 2\n"
        "user@email.edu\n"
        "----------commit-delimiter----------\n"
    )
    mocker.patch("commitizen.cmd.run", return_value=FakeCommand(out=raw_commit))

    commits = git.get_commits()

    assert commits[0].author == "GitHub Action"
    assert commits[1].author == "User"
    assert commits[2].author == "User 2"

    assert commits[0].author_email == "action@github.com"
    assert commits[1].author_email == "user@email.com"
    assert commits[2].author_email == "user@email.edu"

    assert commits[0].title == "bump: version 2.13.0 → 2.14.0"
    assert commits[1].title == "Merge pull request #332 from cliles/feature/271-redux"
    assert (
        commits[2].title == "feat(#271): enable creation of annotated tags when bumping"
    )


def test_get_commits_with_signature():
    config_file = ".git/config"
    config_backup = ".git/config.bak"
    shutil.copy(config_file, config_backup)

    try:
        # temporarily turn on --show-signature
        cmd.run("git config log.showsignature true")

        # retrieve a commit that we know has a signature
        commit = git.get_commits(
            start="bec20ebf433f2281c70f1eb4b0b6a1d0ed83e9b2",
            end="9eae518235d051f145807ddf971ceb79ad49953a",
        )[0]

        assert commit.title.startswith("fix")
    finally:
        # restore the repo's original config
        shutil.move(config_backup, config_file)


def test_get_tag_names_has_correct_arrow_annotation():
    arrow_annotation = inspect.getfullargspec(git.get_tag_names).annotations["return"]

    assert arrow_annotation == "list[str | None]"


def test_get_latest_tag_name(tmp_commitizen_project):
    with tmp_commitizen_project.as_cwd():
        tag_name = git.get_latest_tag_name()
        assert tag_name is None

        create_file_and_commit("feat(test): test")
        cmd.run("git tag 1.0")
        tag_name = git.get_latest_tag_name()
        assert tag_name == "1.0"


def test_is_staging_clean_when_adding_file(tmp_commitizen_project):
    with tmp_commitizen_project.as_cwd():
        assert git.is_staging_clean() is True

        cmd.run("touch test_file")

        assert git.is_staging_clean() is True

        cmd.run("git add test_file")

        assert git.is_staging_clean() is False


def test_is_staging_clean_when_updating_file(tmp_commitizen_project):
    with tmp_commitizen_project.as_cwd():
        assert git.is_staging_clean() is True

        cmd.run("touch test_file")
        cmd.run("git add test_file")
        if os.name == "nt":
            cmd.run('git commit -m "add test_file"')
        else:
            cmd.run("git commit -m 'add test_file'")
        cmd.run("echo 'test' > test_file")

        assert git.is_staging_clean() is True

        cmd.run("git add test_file")

        assert git.is_staging_clean() is False


def test_git_eol_style(tmp_commitizen_project):
    with tmp_commitizen_project.as_cwd():
        assert git.get_eol_style() == git.EOLTypes.NATIVE

        cmd.run("git config core.eol lf")
        assert git.get_eol_style() == git.EOLTypes.LF

        cmd.run("git config core.eol crlf")
        assert git.get_eol_style() == git.EOLTypes.CRLF

        cmd.run("git config core.eol native")
        assert git.get_eol_style() == git.EOLTypes.NATIVE


def test_eoltypes_get_eol_for_open():
    assert git.EOLTypes.get_eol_for_open(git.EOLTypes.NATIVE) == os.linesep
    assert git.EOLTypes.get_eol_for_open(git.EOLTypes.LF) == "\n"
    assert git.EOLTypes.get_eol_for_open(git.EOLTypes.CRLF) == "\r\n"


def test_create_tag_with_message(tmp_commitizen_project):
    with tmp_commitizen_project.as_cwd():
        create_file_and_commit("feat(test): test")
        tag_name = "1.0"
        tag_message = "test message"
        create_tag(tag_name, tag_message)
        assert git.get_latest_tag_name() == tag_name
        assert git.get_tag_message(tag_name) == (
            tag_message if platform.system() != "Windows" else f"'{tag_message}'"
        )
