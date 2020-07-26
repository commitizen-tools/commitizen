import pytest

from commitizen import git
from tests.utils import create_file_and_commit


class FakeCommand:
    def __init__(self, out=None, err=None):
        self.out = out
        self.err = err


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
