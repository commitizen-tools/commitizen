from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING, Any

import pytest

from commitizen import commands, git
from commitizen.cz import registry
from commitizen.cz.base import BaseCommitizen
from commitizen.exceptions import (
    CommitMessageLengthExceededError,
    InvalidCommandArgumentError,
    InvalidCommitMessageError,
    NoCommitsFoundError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pytest_mock import MockFixture, MockType

    from commitizen.config.base_config import BaseConfig
    from commitizen.question import CzQuestion
    from tests.utils import UtilFixture


COMMIT_LOG = [
    "refactor: A code change that neither fixes a bug nor adds a feature",
    r"refactor(cz/conventional_commit): use \S to check scope",
    "refactor(git): remove unnecessary dot between git range",
    "bump: version 1.16.3 → 1.16.4",
    (
        "Merge pull request #139 from Lee-W/fix-init-clean-config-file\n\n"
        "Fix init clean config file"
    ),
    "ci(pyproject.toml): add configuration for coverage",
    "fix(commands/init): fix clean up file when initialize commitizen config\n\n#138",
    "refactor(defaults): split config files into long term support and deprecated ones",
    "bump: version 1.16.2 → 1.16.3",
    (
        "Merge pull request #136 from Lee-W/remove-redundant-readme\n\n"
        "Remove redundant readme"
    ),
    "fix: replace README.rst with docs/README.md in config files",
    (
        "refactor(docs): remove README.rst and use docs/README.md\n\n"
        "By removing README.rst, we no longer need to maintain "
        "two document with almost the same content\n"
        "Github can read docs/README.md as README for the project."
    ),
    "docs(check): pin pre-commit to v1.16.2",
    "docs(check): fix pre-commit setup",
    "bump: version 1.16.1 → 1.16.2",
    "Merge pull request #135 from Lee-W/fix-pre-commit-hook\n\nFix pre commit hook",
    "docs(check): enforce cz check only when committing",
    (
        'Revert "fix(pre-commit): set pre-commit check stage to commit-msg"\n\n'
        "This reverts commit afc70133e4a81344928561fbf3bb20738dfc8a0b."
    ),
    "feat!: add user stuff",
    "fixup! test(commands): ignore fixup! prefix",
    "fixup! test(commands): ignore squash! prefix",
]


def _build_fake_git_commits(commit_msgs: list[str]) -> list[git.GitCommit]:
    return [git.GitCommit("test_rev", commit_msg) for commit_msg in commit_msgs]


def test_check_jira_fails(mocker: MockFixture, util: UtilFixture):
    mock_path = mocker.patch("commitizen.commands.check.Path")
    mock_path.return_value.read_text.return_value = (
        "random message for J-2 #fake_command blah"
    )
    with pytest.raises(InvalidCommitMessageError) as excinfo:
        util.run_cli("-n", "cz_jira", "check", "--commit-msg-file", "some_file")
    assert "commit validation: failed!" in str(excinfo.value)


@pytest.mark.parametrize(
    "commit_msg",
    [
        "JR-23 #command some arguments etc",
        "JR-2  #command some arguments etc",
        "JR-234 some text #command some arguments etc",
        "JRA-23 some text #command1 args #command2 args",
    ],
)
def test_check_jira_command_after_issue(
    mocker: MockFixture, capsys, util: UtilFixture, commit_msg: str
):
    mock_path = mocker.patch("commitizen.commands.check.Path")
    mock_path.return_value.read_text.return_value = commit_msg
    util.run_cli("-n", "cz_jira", "check", "--commit-msg-file", "some_file")
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_conventional_commit_succeeds(
    mocker: MockFixture, capsys, util: UtilFixture
):
    mock_path = mocker.patch("commitizen.commands.check.Path")
    mock_path.return_value.read_text.return_value = "fix(scope): some commit message"
    util.run_cli("check", "--commit-msg-file", "some_file")
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


@pytest.mark.parametrize(
    "commit_msg",
    [
        "feat!(lang): removed polish language",
        "no conventional commit",
        (
            "ci: check commit message on merge\n"
            "testing with more complex commit mes\n\n"
            "age with error"
        ),
    ],
)
def test_check_no_conventional_commit(commit_msg, config, tmpdir):
    tempfile = tmpdir.join("temp_commit_file")
    tempfile.write(commit_msg)

    with pytest.raises(InvalidCommitMessageError):
        commands.Check(config=config, arguments={"commit_msg_file": tempfile})()


@pytest.mark.parametrize(
    "commit_msg",
    [
        "feat(lang)!: removed polish language",
        "feat(lang): added polish language",
        "feat: add polish language",
        "bump: 0.0.1 -> 1.0.0",
    ],
)
def test_check_conventional_commit(commit_msg, config, success_mock: MockType, tmpdir):
    tempfile = tmpdir.join("temp_commit_file")
    tempfile.write(commit_msg)
    commands.Check(config=config, arguments={"commit_msg_file": tempfile})()
    success_mock.assert_called_once()


def test_check_command_when_commit_file_not_found(config):
    with pytest.raises(FileNotFoundError):
        commands.Check(config=config, arguments={"commit_msg_file": "no_such_file"})()


def test_check_a_range_of_git_commits(
    config, success_mock: MockType, mocker: MockFixture
):
    mocker.patch(
        "commitizen.git.get_commits", return_value=_build_fake_git_commits(COMMIT_LOG)
    )

    commands.Check(config=config, arguments={"rev_range": "HEAD~10..master"})()
    success_mock.assert_called_once()


def test_check_a_range_of_git_commits_and_failed(config, mocker: MockFixture):
    mocker.patch(
        "commitizen.git.get_commits",
        return_value=_build_fake_git_commits(["This commit does not follow rule"]),
    )

    with pytest.raises(InvalidCommitMessageError) as excinfo:
        commands.Check(config=config, arguments={"rev_range": "HEAD~10..master"})()
    assert "This commit does not follow rule" in str(excinfo.value)


def test_check_command_with_invalid_argument(config):
    with pytest.raises(InvalidCommandArgumentError) as excinfo:
        commands.Check(
            config=config,
            arguments={"commit_msg_file": "some_file", "rev_range": "HEAD~10..master"},
        )
    assert (
        "Only one of --rev-range, --message, and --commit-msg-file is permitted by check command!"
        in str(excinfo.value)
    )


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_check_command_with_empty_range(config: BaseConfig, util: UtilFixture):
    # must initialize git with a commit
    util.create_file_and_commit("feat: initial")
    with pytest.raises(NoCommitsFoundError) as excinfo:
        commands.Check(config=config, arguments={"rev_range": "master..master"})()
    assert "No commit found with range: 'master..master'" in str(excinfo)


def test_check_a_range_of_failed_git_commits(config, mocker: MockFixture):
    ill_formatted_commits_msgs = [
        "First commit does not follow rule",
        "Second commit does not follow rule",
        ("Third commit does not follow rule\nIll-formatted commit with body"),
    ]
    mocker.patch(
        "commitizen.git.get_commits",
        return_value=_build_fake_git_commits(ill_formatted_commits_msgs),
    )

    with pytest.raises(InvalidCommitMessageError) as excinfo:
        commands.Check(config=config, arguments={"rev_range": "HEAD~10..master"})()
    assert all([msg in str(excinfo.value) for msg in ill_formatted_commits_msgs])


def test_check_command_with_valid_message(config, success_mock: MockType):
    commands.Check(
        config=config, arguments={"message": "fix(scope): some commit message"}
    )()
    success_mock.assert_called_once()


@pytest.mark.parametrize("message", ["bad commit", ""])
def test_check_command_with_invalid_message(config, message):
    with pytest.raises(InvalidCommitMessageError):
        commands.Check(config=config, arguments={"message": message})()


def test_check_command_with_allow_abort_arg(config, success_mock):
    commands.Check(config=config, arguments={"message": "", "allow_abort": True})()
    success_mock.assert_called_once()


def test_check_command_with_allow_abort_config(config, success_mock):
    config.settings["allow_abort"] = True
    commands.Check(config=config, arguments={"message": ""})()
    success_mock.assert_called_once()


def test_check_command_override_allow_abort_config(config):
    config.settings["allow_abort"] = True
    with pytest.raises(InvalidCommitMessageError):
        commands.Check(config=config, arguments={"message": "", "allow_abort": False})()


def test_check_command_with_allowed_prefixes_arg(config, success_mock):
    commands.Check(
        config=config,
        arguments={"message": "custom! test", "allowed_prefixes": ["custom!"]},
    )()
    success_mock.assert_called_once()


def test_check_command_with_allowed_prefixes_config(config, success_mock):
    config.settings["allowed_prefixes"] = ["custom!"]
    commands.Check(config=config, arguments={"message": "custom! test"})()
    success_mock.assert_called_once()


def test_check_command_override_allowed_prefixes_config(config):
    config.settings["allow_abort"] = ["fixup!"]
    with pytest.raises(InvalidCommitMessageError):
        commands.Check(
            config=config,
            arguments={"message": "fixup! test", "allowed_prefixes": ["custom!"]},
        )()


def test_check_command_with_pipe_message(
    mocker: MockFixture, capsys, util: UtilFixture
):
    mocker.patch("sys.stdin", StringIO("fix(scope): some commit message"))

    util.run_cli("check")
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_command_with_pipe_message_and_failed(
    mocker: MockFixture, util: UtilFixture
):
    mocker.patch("sys.stdin", StringIO("bad commit message"))

    with pytest.raises(InvalidCommitMessageError) as excinfo:
        util.run_cli("check")
    assert "commit validation: failed!" in str(excinfo.value)


def test_check_command_with_comment_in_message_file(
    mocker: MockFixture, capsys, util: UtilFixture
):
    mock_path = mocker.patch("commitizen.commands.check.Path")
    mock_path.return_value.read_text.return_value = (
        "# <type>: (If applied, this commit will...) <subject>\n"
        "# |<---- Try to Limit to a Max of 50 char ---->|\n"
        "ci: add commitizen pre-commit hook\n"
        "\n"
        "# Explain why this change is being made\n"
        "# |<---- Try To Limit Each Line to a Max Of 72 Char ---->|\n"
        "This pre-commit hook will check our commits automatically."
    )
    util.run_cli("check", "--commit-msg-file", "some_file")
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_conventional_commit_succeed_with_git_diff(
    mocker, capsys, util: UtilFixture
):
    mock_path = mocker.patch("commitizen.commands.check.Path")
    mock_path.return_value.read_text.return_value = (
        "feat: This is a test commit\n"
        "# Please enter the commit message for your changes. Lines starting\n"
        "# with '#' will be ignored, and an empty message aborts the commit.\n"
        "#\n"
        "# On branch ...\n"
        "# Changes to be committed:\n"
        "#	modified:  ...\n"
        "#\n"
        "# ------------------------ >8 ------------------------\n"
        "# Do not modify or remove the line above.\n"
        "# Everything below it will be ignored.\n"
        "diff --git a/... b/...\n"
        "index f1234c..1c5678 1234\n"
        "--- a/...\n"
        "+++ b/...\n"
        "@@ -92,3 +92,4 @@ class Command(BaseCommand):\n"
        '+            "this is a test"\n'
    )
    util.run_cli("check", "--commit-msg-file", "some_file")
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_command_with_message_length_limit(config, success_mock):
    message = "fix(scope): some commit message"
    commands.Check(
        config=config,
        arguments={"message": message, "message_length_limit": len(message) + 1},
    )()
    success_mock.assert_called_once()


def test_check_command_with_message_length_limit_exceeded(config):
    message = "fix(scope): some commit message"
    with pytest.raises(CommitMessageLengthExceededError):
        commands.Check(
            config=config,
            arguments={"message": message, "message_length_limit": len(message) - 1},
        )()


def test_check_command_with_amend_prefix_default(config, success_mock):
    commands.Check(config=config, arguments={"message": "amend! test"})()
    success_mock.assert_called_once()


def test_check_command_with_config_message_length_limit(config, success_mock):
    message = "fix(scope): some commit message"
    config.settings["message_length_limit"] = len(message) + 1
    commands.Check(
        config=config,
        arguments={"message": message},
    )()
    success_mock.assert_called_once()


def test_check_command_with_config_message_length_limit_exceeded(config):
    message = "fix(scope): some commit message"
    config.settings["message_length_limit"] = len(message) - 1
    with pytest.raises(CommitMessageLengthExceededError):
        commands.Check(
            config=config,
            arguments={"message": message},
        )()


def test_check_command_cli_overrides_config_message_length_limit(
    config, success_mock: MockType
):
    message = "fix(scope): some commit message"
    config.settings["message_length_limit"] = len(message) - 1
    for message_length_limit in [len(message) + 1, 0]:
        success_mock.reset_mock()
        commands.Check(
            config=config,
            arguments={
                "message": message,
                "message_length_limit": message_length_limit,
            },
        )()
        success_mock.assert_called_once()


class ValidationCz(BaseCommitizen):
    def questions(self) -> list[CzQuestion]:
        return [
            {"type": "input", "name": "commit", "message": "Initial commit:\n"},
            {"type": "input", "name": "issue_nb", "message": "ABC-123"},
        ]

    def message(self, answers: Mapping[str, Any]) -> str:
        return f"{answers['issue_nb']}: {answers['commit']}"

    def schema(self) -> str:
        return "<issue_nb>: <commit>"

    def schema_pattern(self) -> str:
        return r"^(?P<issue_nb>[A-Z]{3}-\d+): (?P<commit>.*)$"

    def example(self) -> str:
        return "ABC-123: fixed a bug"

    def info(self) -> str:
        return "Commit message must start with an issue number like ABC-123"


@pytest.fixture
def use_cz_custom_validator(mocker):
    new_cz = {**registry, "cz_custom_validator": ValidationCz}
    mocker.patch.dict("commitizen.cz.registry", new_cz)


@pytest.mark.usefixtures("use_cz_custom_validator")
def test_check_command_with_custom_validator_succeed(
    mocker: MockFixture, capsys, util: UtilFixture
):
    mock_path = mocker.patch("commitizen.commands.check.Path")
    mock_path.return_value.read_text.return_value = (
        "ABC-123: add commitizen pre-commit hook"
    )
    util.run_cli(
        "--name", "cz_custom_validator", "check", "--commit-msg-file", "some_file"
    )
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


@pytest.mark.usefixtures("use_cz_custom_validator")
def test_check_command_with_custom_validator_failed(
    mocker: MockFixture, util: UtilFixture
):
    mock_path = mocker.patch("commitizen.commands.check.Path")
    mock_path.return_value.read_text.return_value = (
        "123-ABC issue id has wrong format and misses colon"
    )
    with pytest.raises(InvalidCommitMessageError) as excinfo:
        util.run_cli(
            "--name", "cz_custom_validator", "check", "--commit-msg-file", "some_file"
        )
    assert "commit validation: failed!" in str(excinfo.value), (
        "Pattern validation unexpectedly passed"
    )
    assert "pattern: " in str(excinfo.value), "Pattern not found in error message"
