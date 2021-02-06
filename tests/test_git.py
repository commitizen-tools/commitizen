import inspect
from typing import List, Optional

import pytest

from commitizen import cmd, git
from tests.utils import FakeCommand, create_file_and_commit


def test_git_object_eq():
    git_commit = git.GitCommit(
        rev="sha1-code", title="this is title", body="this is body"
    )
    git_tag = git.GitTag(rev="sha1-code", name="0.0.1", date="2020-01-21")

    assert git_commit == git_tag
    assert git_commit != "sha1-code"


def test_get_tags(mocker):
    tag_str = (
        "v1.0.0---inner_delimiter---333---inner_delimiter---2020-01-20\n"
        "v0.5.0---inner_delimiter---222---inner_delimiter---2020-01-17\n"
        "v0.0.1---inner_delimiter---111---inner_delimiter---2020-01-17\n"
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


def test_get_tag_names(mocker):
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
def test_get_commits():
    create_file_and_commit("feat(users): add username")
    create_file_and_commit("fix: username exception")
    commits = git.get_commits()
    assert len(commits) == 2


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_get_commits_author_and_email():
    create_file_and_commit("fix: username exception")
    commit = git.get_commits()[0]

    assert commit.author is not ""
    assert "@" in commit.author_email


def test_get_commits_without_email(mocker):
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


def test_get_tag_names_has_correct_arrow_annotation():
    arrow_annotation = inspect.getfullargspec(git.get_tag_names).annotations["return"]

    assert arrow_annotation == List[Optional[str]]


def test_get_latest_tag_name(tmp_commitizen_project):
    with tmp_commitizen_project.as_cwd():
        tag_name = git.get_latest_tag_name()
        assert tag_name is None

        create_file_and_commit("feat(test): test")
        cmd.run("git tag 1.0")
        tag_name = git.get_latest_tag_name()
        assert tag_name == "1.0"
