from commitizen import git


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
