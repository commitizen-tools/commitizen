from commitizen import git


def test_git_object_eq():
    git_commit = git.GitCommit(
        rev="sha1-code", title="this is title", body="this is body"
    )
    git_tag = git.GitTag(rev="sha1-code", name="0.0.1", date="2020-01-21")

    assert git_commit == git_tag
    assert git_commit != "sha1-code"
