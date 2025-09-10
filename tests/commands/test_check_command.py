from __future__ import annotations

import sys
from io import StringIO

import pytest
from pytest_mock import MockFixture

from commitizen import cli, commands, git
from commitizen.exceptions import (
    InvalidCommandArgumentError,
    InvalidCommitMessageError,
    NoCommitsFoundError,
)
from tests.utils import create_file_and_commit, skip_below_py_3_13

COMMIT_LOG = [
    "refactor: A code change that neither fixes a bug nor adds a feature",
    r"refactor(cz/connventional_commit): use \S to check scope",
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


def test_check_jira_fails(mocker: MockFixture):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="random message for J-2 #fake_command blah"),
    )
    with pytest.raises(InvalidCommitMessageError) as excinfo:
        cli.main()
    assert "commit validation: failed!" in str(excinfo.value)


def test_check_jira_command_after_issue_one_space(mocker: MockFixture, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JR-23 #command some arguments etc"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_jira_command_after_issue_two_spaces(mocker: MockFixture, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JR-2  #command some arguments etc"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_jira_text_between_issue_and_command(mocker: MockFixture, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JR-234 some text #command some arguments etc"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_jira_multiple_commands(mocker: MockFixture, capsys):
    testargs = ["cz", "-n", "cz_jira", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="JRA-23 some text #command1 args #command2 args"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_conventional_commit_succeeds(mocker: MockFixture, capsys):
    testargs = ["cz", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data="fix(scope): some commit message"),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


@pytest.mark.parametrize(
    "commit_msg",
    (
        "feat!(lang): removed polish language",
        "no conventional commit",
        (
            "ci: check commit message on merge\n"
            "testing with more complex commit mes\n\n"
            "age with error"
        ),
    ),
)
def test_check_no_conventional_commit(commit_msg, config, mocker: MockFixture, tmpdir):
    with pytest.raises(InvalidCommitMessageError):
        error_mock = mocker.patch("commitizen.out.error")

        tempfile = tmpdir.join("temp_commit_file")
        tempfile.write(commit_msg)

        check_cmd = commands.Check(
            config=config, arguments={"commit_msg_file": tempfile}
        )
        check_cmd()
        error_mock.assert_called_once()


@pytest.mark.parametrize(
    "commit_msg",
    (
        "feat(lang)!: removed polish language",
        "feat(lang): added polish language",
        "feat: add polish language",
        "bump: 0.0.1 -> 1.0.0",
    ),
)
def test_check_conventional_commit(commit_msg, config, mocker: MockFixture, tmpdir):
    success_mock = mocker.patch("commitizen.out.success")

    tempfile = tmpdir.join("temp_commit_file")
    tempfile.write(commit_msg)

    check_cmd = commands.Check(config=config, arguments={"commit_msg_file": tempfile})

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_when_commit_file_not_found(config):
    with pytest.raises(FileNotFoundError):
        commands.Check(config=config, arguments={"commit_msg_file": "no_such_file"})()


def test_check_a_range_of_git_commits(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    mocker.patch(
        "commitizen.git.get_commits", return_value=_build_fake_git_commits(COMMIT_LOG)
    )

    check_cmd = commands.Check(
        config=config, arguments={"rev_range": "HEAD~10..master"}
    )

    check_cmd()
    success_mock.assert_called_once()


def test_check_a_range_of_git_commits_and_failed(config, mocker: MockFixture):
    error_mock = mocker.patch("commitizen.out.error")
    mocker.patch(
        "commitizen.git.get_commits",
        return_value=_build_fake_git_commits(["This commit does not follow rule"]),
    )
    check_cmd = commands.Check(
        config=config, arguments={"rev_range": "HEAD~10..master"}
    )

    with pytest.raises(InvalidCommitMessageError):
        check_cmd()
        error_mock.assert_called_once()


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
def test_check_command_with_empty_range(config, mocker: MockFixture):
    # must initialize git with a commit
    create_file_and_commit("feat: initial")

    check_cmd = commands.Check(config=config, arguments={"rev_range": "master..master"})
    with pytest.raises(NoCommitsFoundError) as excinfo:
        check_cmd()

    assert "No commit found with range: 'master..master'" in str(excinfo)


def test_check_a_range_of_failed_git_commits(config, mocker: MockFixture):
    ill_formated_commits_msgs = [
        "First commit does not follow rule",
        "Second commit does not follow rule",
        ("Third commit does not follow rule\nIll-formatted commit with body"),
    ]
    mocker.patch(
        "commitizen.git.get_commits",
        return_value=_build_fake_git_commits(ill_formated_commits_msgs),
    )
    check_cmd = commands.Check(
        config=config, arguments={"rev_range": "HEAD~10..master"}
    )

    with pytest.raises(InvalidCommitMessageError) as excinfo:
        check_cmd()
    assert all([msg in str(excinfo.value) for msg in ill_formated_commits_msgs])


def test_check_command_with_valid_message(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    check_cmd = commands.Check(
        config=config, arguments={"message": "fix(scope): some commit message"}
    )

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_with_invalid_message(config, mocker: MockFixture):
    error_mock = mocker.patch("commitizen.out.error")
    check_cmd = commands.Check(config=config, arguments={"message": "bad commit"})

    with pytest.raises(InvalidCommitMessageError):
        check_cmd()
        error_mock.assert_called_once()


def test_check_command_with_empty_message(config, mocker: MockFixture):
    error_mock = mocker.patch("commitizen.out.error")
    check_cmd = commands.Check(config=config, arguments={"message": ""})

    with pytest.raises(InvalidCommitMessageError):
        check_cmd()
        error_mock.assert_called_once()


def test_check_command_with_allow_abort_arg(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    check_cmd = commands.Check(
        config=config, arguments={"message": "", "allow_abort": True}
    )

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_with_allow_abort_config(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    config.settings["allow_abort"] = True
    check_cmd = commands.Check(config=config, arguments={"message": ""})

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_override_allow_abort_config(config, mocker: MockFixture):
    error_mock = mocker.patch("commitizen.out.error")
    config.settings["allow_abort"] = True
    check_cmd = commands.Check(
        config=config, arguments={"message": "", "allow_abort": False}
    )

    with pytest.raises(InvalidCommitMessageError):
        check_cmd()
        error_mock.assert_called_once()


def test_check_command_with_allowed_prefixes_arg(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    check_cmd = commands.Check(
        config=config,
        arguments={"message": "custom! test", "allowed_prefixes": ["custom!"]},
    )

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_with_allowed_prefixes_config(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    config.settings["allowed_prefixes"] = ["custom!"]
    check_cmd = commands.Check(config=config, arguments={"message": "custom! test"})

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_override_allowed_prefixes_config(config, mocker: MockFixture):
    error_mock = mocker.patch("commitizen.out.error")
    config.settings["allow_abort"] = ["fixup!"]
    check_cmd = commands.Check(
        config=config,
        arguments={"message": "fixup! test", "allowed_prefixes": ["custom!"]},
    )

    with pytest.raises(InvalidCommitMessageError):
        check_cmd()
        error_mock.assert_called_once()


def test_check_command_with_pipe_message(mocker: MockFixture, capsys):
    testargs = ["cz", "check"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch("sys.stdin", StringIO("fix(scope): some commit message"))

    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_command_with_pipe_message_and_failed(mocker: MockFixture):
    testargs = ["cz", "check"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch("sys.stdin", StringIO("bad commit message"))

    with pytest.raises(InvalidCommitMessageError) as excinfo:
        cli.main()
    assert "commit validation: failed!" in str(excinfo.value)


def test_check_command_with_comment_in_message_file(mocker: MockFixture, capsys):
    testargs = ["cz", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(
            read_data="# <type>: (If applied, this commit will...) <subject>\n"
            "# |<---- Try to Limit to a Max of 50 char ---->|\n"
            "ci: add commitizen pre-commit hook\n"
            "\n"
            "# Explain why this change is being made\n"
            "# |<---- Try To Limit Each Line to a Max Of 72 Char ---->|\n"
            "This pre-commit hook will check our commits automatically."
        ),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


def test_check_conventional_commit_succeed_with_git_diff(mocker, capsys):
    commit_msg = (
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
    testargs = ["cz", "check", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)
    mocker.patch(
        "commitizen.commands.check.open",
        mocker.mock_open(read_data=commit_msg),
    )
    cli.main()
    out, _ = capsys.readouterr()
    assert "Commit validation: successful!" in out


@skip_below_py_3_13
def test_check_command_shows_description_when_use_help_option(
    mocker: MockFixture, capsys, file_regression
):
    testargs = ["cz", "check", "--help"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".txt")


def test_check_command_with_message_length_limit(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    message = "fix(scope): some commit message"
    check_cmd = commands.Check(
        config=config,
        arguments={"message": message, "message_length_limit": len(message) + 1},
    )

    check_cmd()
    success_mock.assert_called_once()


def test_check_command_with_message_length_limit_exceeded(config, mocker: MockFixture):
    error_mock = mocker.patch("commitizen.out.error")
    message = "fix(scope): some commit message"
    check_cmd = commands.Check(
        config=config,
        arguments={"message": message, "message_length_limit": len(message) - 1},
    )

    with pytest.raises(InvalidCommitMessageError):
        check_cmd()
        error_mock.assert_called_once()


def test_check_command_with_amend_prefix_default(config, mocker: MockFixture):
    success_mock = mocker.patch("commitizen.out.success")
    check_cmd = commands.Check(config=config, arguments={"message": "amend! test"})

    check_cmd()
    success_mock.assert_called_once()
