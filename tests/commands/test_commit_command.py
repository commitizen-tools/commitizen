import os
from unittest.mock import ANY

import pytest
from pytest_mock import MockFixture, MockType

from commitizen import cmd, commands
from commitizen.cz.exceptions import CzException
from commitizen.cz.utils import get_backup_file_path
from commitizen.exceptions import (
    CommitError,
    CommitMessageLengthExceededError,
    CustomError,
    DryRunExit,
    NoAnswersError,
    NoCommitBackupError,
    NotAGitProjectError,
    NotAllowed,
    NothingToCommitError,
)


@pytest.fixture
def commit_mock(mocker: MockFixture):
    return mocker.patch(
        "commitizen.git.commit", return_value=cmd.Command("success", "", b"", b"", 0)
    )


@pytest.fixture
def prompt_mock_feat(mocker: MockFixture):
    return mocker.patch(
        "questionary.prompt",
        return_value={
            "prefix": "feat",
            "subject": "user created",
            "scope": "",
            "is_breaking_change": False,
            "body": "closes #21",
            "footer": "",
        },
    )


@pytest.fixture
def staging_is_clean(mocker: MockFixture, tmp_git_project):
    mocker.patch("commitizen.git.is_staging_clean", return_value=False)
    return tmp_git_project


@pytest.fixture
def backup_file(tmp_git_project):
    with open(get_backup_file_path(), "w") as backup_file:
        backup_file.write("backup commit")


@pytest.mark.usefixtures("staging_is_clean", "commit_mock", "prompt_mock_feat")
def test_commit(config, success_mock: MockType):
    commands.Commit(config, {})()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_backup_on_failure(
    config, mocker: MockFixture, prompt_mock_feat: MockType
):
    mocker.patch(
        "commitizen.git.commit", return_value=cmd.Command("", "error", b"", b"", 9)
    )
    error_mock = mocker.patch("commitizen.out.error")

    commit_cmd = commands.Commit(config, {})
    temp_file = commit_cmd.backup_file_path
    with pytest.raises(CommitError):
        commit_cmd()

    prompt_mock_feat.assert_called_once()
    error_mock.assert_called_once()
    assert os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean", "commit_mock")
def test_commit_retry_fails_no_backup(config):
    with pytest.raises(NoCommitBackupError) as excinfo:
        commands.Commit(config, {"retry": True})()

    assert NoCommitBackupError.message in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_works(
    config, success_mock: MockType, mocker: MockFixture, commit_mock: MockType
):
    prompt_mock = mocker.patch("questionary.prompt")

    commit_cmd = commands.Commit(config, {"retry": True})
    temp_file = commit_cmd.backup_file_path
    commit_cmd()

    commit_mock.assert_called_with("backup commit", args="")
    prompt_mock.assert_not_called()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_after_failure_no_backup(
    config, success_mock: MockType, commit_mock: MockType, prompt_mock_feat: MockType
):
    config.settings["retry_after_failure"] = True
    commands.Commit(config, {})()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21", args="")
    prompt_mock_feat.assert_called_once()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_after_failure_works(
    config, success_mock: MockType, mocker: MockFixture, commit_mock: MockType
):
    prompt_mock = mocker.patch("questionary.prompt")

    config.settings["retry_after_failure"] = True
    commit_cmd = commands.Commit(config, {})
    temp_file = commit_cmd.backup_file_path
    commit_cmd()

    commit_mock.assert_called_with("backup commit", args="")
    prompt_mock.assert_not_called()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_after_failure_with_no_retry_works(
    config, success_mock: MockType, commit_mock: MockType, prompt_mock_feat: MockType
):
    config.settings["retry_after_failure"] = True
    commit_cmd = commands.Commit(config, {"no_retry": True})
    temp_file = commit_cmd.backup_file_path
    commit_cmd()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21", args="")
    prompt_mock_feat.assert_called_once()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_dry_run_option(config):
    with pytest.raises(DryRunExit):
        commands.Commit(config, {"dry_run": True})()


@pytest.mark.usefixtures("staging_is_clean", "commit_mock", "prompt_mock_feat")
def test_commit_command_with_write_message_to_file_option(
    config, tmp_path, success_mock: MockType
):
    tmp_file = tmp_path / "message"
    commands.Commit(config, {"write_message_to_file": tmp_file})()
    success_mock.assert_called_once()
    assert tmp_file.exists()
    assert "feat: user created" in tmp_file.read_text()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_invalid_write_message_to_file_option(config, tmp_path):
    with pytest.raises(NotAllowed):
        commands.Commit(config, {"write_message_to_file": tmp_path})()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_signoff_option(
    config, success_mock: MockType, commit_mock: MockType
):
    commands.Commit(config, {"signoff": True})()

    commit_mock.assert_called_once_with(ANY, args="-s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_always_signoff_enabled(
    config, success_mock: MockType, commit_mock: MockType
):
    config.settings["always_signoff"] = True
    commands.Commit(config, {})()

    commit_mock.assert_called_once_with(ANY, args="-s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_gpgsign_and_always_signoff_enabled(
    config, success_mock: MockType, commit_mock: MockType
):
    config.settings["always_signoff"] = True
    commands.Commit(config, {"extra_cli_args": "-S"})()

    commit_mock.assert_called_once_with(ANY, args="-S -s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("tmp_git_project")
def test_commit_when_nothing_to_commit(config, mocker: MockFixture):
    mocker.patch("commitizen.git.is_staging_clean", return_value=True)

    with pytest.raises(NothingToCommitError) as excinfo:
        commands.Commit(config, {})()

    assert "No files added to staging!" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_with_allow_empty(config, success_mock: MockType, commit_mock: MockType):
    commands.Commit(config, {"extra_cli_args": "--allow-empty"})()
    commit_mock.assert_called_with(
        "feat: user created\n\ncloses #21", args="--allow-empty"
    )
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_with_signoff_and_allow_empty(
    config, success_mock: MockType, commit_mock: MockType
):
    config.settings["always_signoff"] = True
    commands.Commit(config, {"extra_cli_args": "--allow-empty"})()

    commit_mock.assert_called_with(
        "feat: user created\n\ncloses #21", args="--allow-empty -s"
    )
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_customized_expected_raised(config, mocker: MockFixture):
    _err = ValueError()
    _err.__context__ = CzException("This is the root custom err")
    mocker.patch("questionary.prompt", side_effect=_err)
    with pytest.raises(CustomError) as excinfo:
        commands.Commit(config, {})()

    # Assert only the content in the formatted text
    assert "This is the root custom err" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_non_customized_expected_raised(config, mocker: MockFixture):
    mocker.patch("questionary.prompt", side_effect=ValueError())
    with pytest.raises(ValueError):
        commands.Commit(config, {})()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_no_user_answer(config, mocker: MockFixture):
    mocker.patch("questionary.prompt", return_value=None)
    with pytest.raises(NoAnswersError):
        commands.Commit(config, {})()


def test_commit_in_non_git_project(tmpdir, config):
    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            commands.Commit(config, {})


@pytest.mark.usefixtures("staging_is_clean", "commit_mock", "prompt_mock_feat")
def test_commit_command_with_all_option(
    config, success_mock: MockType, mocker: MockFixture
):
    add_mock = mocker.patch("commitizen.git.add")
    commands.Commit(config, {"all": True})()
    add_mock.assert_called()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_extra_args(
    config, success_mock: MockType, commit_mock: MockType
):
    commands.Commit(config, {"extra_cli_args": "-- -extra-args1 -extra-arg2"})()
    commit_mock.assert_called_once_with(ANY, args="-- -extra-args1 -extra-arg2")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
@pytest.mark.parametrize("editor", ["vim", None])
def test_manual_edit(editor, config, mocker: MockFixture, tmp_path):
    mocker.patch("commitizen.git.get_core_editor", return_value=editor)
    subprocess_mock = mocker.patch("subprocess.call")

    mocker.patch("shutil.which", return_value=editor)

    test_message = "Initial commit message"
    temp_file = tmp_path / "temp_commit_message"
    temp_file.write_text(test_message)

    mock_temp_file = mocker.patch("tempfile.NamedTemporaryFile")
    mock_temp_file.return_value.__enter__.return_value.name = str(temp_file)

    commit_cmd = commands.Commit(config, {"edit": True})

    if editor is None:
        with pytest.raises(RuntimeError):
            commit_cmd.manual_edit(test_message)
    else:
        edited_message = commit_cmd.manual_edit(test_message)
        subprocess_mock.assert_called_once_with(["vim", str(temp_file)])
        assert edited_message == test_message.strip()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
@pytest.mark.parametrize(
    "out", ["no changes added to commit", "nothing added to commit"]
)
def test_commit_when_nothing_added_to_commit(config, mocker: MockFixture, out):
    commit_mock = mocker.patch(
        "commitizen.git.commit",
        return_value=cmd.Command(
            out=out,
            err="",
            stdout=out.encode(),
            stderr=b"",
            return_code=0,
        ),
    )
    error_mock = mocker.patch("commitizen.out.error")

    commands.Commit(config, {})()

    commit_mock.assert_called_once()
    error_mock.assert_called_once_with(out)


@pytest.mark.usefixtures("staging_is_clean", "commit_mock")
def test_commit_command_with_config_message_length_limit(
    config, success_mock: MockType, prompt_mock_feat: MockType
):
    message_length = (
        len(prompt_mock_feat.return_value["prefix"])
        + len(": ")
        + len(prompt_mock_feat.return_value["subject"])
    )

    commands.Commit(config, {"message_length_limit": message_length})()
    success_mock.assert_called_once()

    with pytest.raises(CommitMessageLengthExceededError):
        commands.Commit(config, {"message_length_limit": message_length - 1})()

    config.settings["message_length_limit"] = message_length
    success_mock.reset_mock()
    commands.Commit(config, {})()
    success_mock.assert_called_once()

    config.settings["message_length_limit"] = message_length - 1
    with pytest.raises(CommitMessageLengthExceededError):
        commands.Commit(config, {})()

    # Test config message length limit is overridden by CLI argument
    success_mock.reset_mock()
    commands.Commit(config, {"message_length_limit": message_length})()
    success_mock.assert_called_once()

    success_mock.reset_mock()
    commands.Commit(config, {"message_length_limit": None})()
    success_mock.assert_called_once()
