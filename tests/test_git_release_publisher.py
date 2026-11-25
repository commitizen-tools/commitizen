import pytest
from pytest_mock import MockerFixture

from commitizen import cmd
from commitizen.commands.bump import GitReleasePublisher
from commitizen.exceptions import BumpCommitFailedError, BumpTagFailedError


def _result(return_code: int) -> cmd.Command:
    err = "error" if return_code else ""
    return cmd.Command(
        out="", err=err, stdout=b"", stderr=err.encode(), return_code=return_code
    )


def _publisher(*, retry: bool = False, no_verify: bool = False) -> GitReleasePublisher:
    return GitReleasePublisher(
        no_verify=no_verify, retry=retry, git_output_to_stderr=False
    )


def test_commit_retries_once_when_changelog_was_updated(mocker: MockerFixture):
    """A pre-commit hook can reformat the changelog, so the second commit succeeds."""
    # Arrange
    mocker.patch("commitizen.git.add")
    commit_mock = mocker.patch(
        "commitizen.git.commit", side_effect=[_result(1), _result(0)]
    )

    # Act
    _publisher(retry=True).commit(
        "bump: 1.0.0 → 1.1.0", ["CHANGELOG.md"], changelog_was_updated=True
    )

    # Assert
    assert commit_mock.call_count == 2


def test_commit_does_not_retry_without_changelog(mocker: MockerFixture):
    # Arrange
    mocker.patch("commitizen.git.add")
    commit_mock = mocker.patch("commitizen.git.commit", return_value=_result(1))

    # Act
    with pytest.raises(BumpCommitFailedError):
        _publisher(retry=True).commit(
            "bump: 1.0.0 → 1.1.0", ["pyproject.toml"], changelog_was_updated=False
        )

    # Assert
    assert commit_mock.call_count == 1


def test_commit_passes_no_verify(mocker: MockerFixture):
    # Arrange
    mocker.patch("commitizen.git.add")
    commit_mock = mocker.patch("commitizen.git.commit", return_value=_result(0))

    # Act
    _publisher(no_verify=True).commit(
        "bump: 1.0.0 → 1.1.0", ["pyproject.toml"], changelog_was_updated=False
    )

    # Assert
    commit_mock.assert_called_once_with(
        "bump: 1.0.0 → 1.1.0", args=["-a", "--no-verify"]
    )


def test_tag_failure_raises(mocker: MockerFixture):
    # Arrange
    mocker.patch("commitizen.git.tag", return_value=_result(1))

    # Act / Assert
    with pytest.raises(BumpTagFailedError):
        _publisher().tag("v1.1.0", signed=False, annotated=False, msg=None)
