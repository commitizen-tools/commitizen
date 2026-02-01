from pathlib import Path
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
def test_commit(default_config, success_mock: MockType):
    commands.Commit(default_config, {})()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_backup_on_failure(
    default_config, mocker: MockFixture, prompt_mock_feat: MockType
):
    mocker.patch(
        "commitizen.git.commit", return_value=cmd.Command("", "error", b"", b"", 9)
    )
    error_mock = mocker.patch("commitizen.out.error")

    commit_cmd = commands.Commit(default_config, {})
    temp_file = commit_cmd.backup_file_path
    with pytest.raises(CommitError):
        commit_cmd()

    prompt_mock_feat.assert_called_once()
    error_mock.assert_called_once()
    assert Path(temp_file).exists()


@pytest.mark.usefixtures("staging_is_clean", "commit_mock")
def test_commit_retry_fails_no_backup(default_config):
    with pytest.raises(NoCommitBackupError) as excinfo:
        commands.Commit(default_config, {"retry": True})()

    assert NoCommitBackupError.message in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_works(
    default_config, success_mock: MockType, mocker: MockFixture, commit_mock: MockType
):
    prompt_mock = mocker.patch("questionary.prompt")

    commit_cmd = commands.Commit(default_config, {"retry": True})
    temp_file = commit_cmd.backup_file_path
    commit_cmd()

    commit_mock.assert_called_with("backup commit", args="")
    prompt_mock.assert_not_called()
    success_mock.assert_called_once()
    assert not Path(temp_file).exists()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_after_failure_no_backup(
    default_config,
    success_mock: MockType,
    commit_mock: MockType,
    prompt_mock_feat: MockType,
):
    default_config.settings["retry_after_failure"] = True
    commands.Commit(default_config, {})()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21", args="")
    prompt_mock_feat.assert_called_once()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_after_failure_works(
    default_config, success_mock: MockType, mocker: MockFixture, commit_mock: MockType
):
    prompt_mock = mocker.patch("questionary.prompt")

    default_config.settings["retry_after_failure"] = True
    commit_cmd = commands.Commit(default_config, {})
    temp_file = commit_cmd.backup_file_path
    commit_cmd()

    commit_mock.assert_called_with("backup commit", args="")
    prompt_mock.assert_not_called()
    success_mock.assert_called_once()
    assert not Path(temp_file).exists()


@pytest.mark.usefixtures("staging_is_clean", "backup_file")
def test_commit_retry_after_failure_with_no_retry_works(
    default_config,
    success_mock: MockType,
    commit_mock: MockType,
    prompt_mock_feat: MockType,
):
    default_config.settings["retry_after_failure"] = True
    commit_cmd = commands.Commit(default_config, {"no_retry": True})
    temp_file = commit_cmd.backup_file_path
    commit_cmd()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21", args="")
    prompt_mock_feat.assert_called_once()
    success_mock.assert_called_once()
    assert not Path(temp_file).exists()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_dry_run_option(default_config):
    with pytest.raises(DryRunExit):
        commands.Commit(default_config, {"dry_run": True})()


@pytest.mark.usefixtures("staging_is_clean", "commit_mock", "prompt_mock_feat")
def test_commit_command_with_write_message_to_file_option(
    default_config, tmp_path, success_mock: MockType
):
    tmp_file = tmp_path / "message"
    commands.Commit(default_config, {"write_message_to_file": tmp_file})()
    success_mock.assert_called_once()
    assert tmp_file.exists()
    assert "feat: user created" in tmp_file.read_text()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_invalid_write_message_to_file_option(
    default_config, tmp_path
):
    with pytest.raises(NotAllowed):
        commands.Commit(default_config, {"write_message_to_file": tmp_path})()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_signoff_option(
    default_config, success_mock: MockType, commit_mock: MockType
):
    commands.Commit(default_config, {"signoff": True})()

    commit_mock.assert_called_once_with(ANY, args="-s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_always_signoff_enabled(
    default_config, success_mock: MockType, commit_mock: MockType
):
    default_config.settings["always_signoff"] = True
    commands.Commit(default_config, {})()

    commit_mock.assert_called_once_with(ANY, args="-s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_gpgsign_and_always_signoff_enabled(
    default_config, success_mock: MockType, commit_mock: MockType
):
    default_config.settings["always_signoff"] = True
    commands.Commit(default_config, {"extra_cli_args": "-S"})()

    commit_mock.assert_called_once_with(ANY, args="-S -s")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("tmp_git_project")
def test_commit_when_nothing_to_commit(default_config, mocker: MockFixture):
    mocker.patch("commitizen.git.is_staging_clean", return_value=True)

    with pytest.raises(NothingToCommitError) as excinfo:
        commands.Commit(default_config, {})()

    assert "No files added to staging!" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_with_allow_empty(
    default_config, success_mock: MockType, commit_mock: MockType
):
    commands.Commit(default_config, {"extra_cli_args": "--allow-empty"})()
    commit_mock.assert_called_with(
        "feat: user created\n\ncloses #21", args="--allow-empty"
    )
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_with_signoff_and_allow_empty(
    default_config, success_mock: MockType, commit_mock: MockType
):
    default_config.settings["always_signoff"] = True
    commands.Commit(default_config, {"extra_cli_args": "--allow-empty"})()

    commit_mock.assert_called_with(
        "feat: user created\n\ncloses #21", args="--allow-empty -s"
    )
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_customized_expected_raised(default_config, mocker: MockFixture):
    _err = ValueError()
    _err.__context__ = CzException("This is the root custom err")
    mocker.patch("questionary.prompt", side_effect=_err)
    with pytest.raises(CustomError) as excinfo:
        commands.Commit(default_config, {})()

    # Assert only the content in the formatted text
    assert "This is the root custom err" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_non_customized_expected_raised(
    default_config, mocker: MockFixture
):
    mocker.patch("questionary.prompt", side_effect=ValueError())
    with pytest.raises(ValueError):
        commands.Commit(default_config, {})()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_no_user_answer(default_config, mocker: MockFixture):
    mocker.patch("questionary.prompt", return_value=None)
    with pytest.raises(NoAnswersError):
        commands.Commit(default_config, {})()


def test_commit_in_non_git_project(tmpdir, default_config):
    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            commands.Commit(default_config, {})


@pytest.mark.usefixtures("staging_is_clean", "commit_mock", "prompt_mock_feat")
def test_commit_command_with_all_option(
    default_config, success_mock: MockType, mocker: MockFixture
):
    add_mock = mocker.patch("commitizen.git.add")
    commands.Commit(default_config, {"all": True})()
    add_mock.assert_called()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean", "prompt_mock_feat")
def test_commit_command_with_extra_args(
    default_config, success_mock: MockType, commit_mock: MockType
):
    commands.Commit(default_config, {"extra_cli_args": "-- -extra-args1 -extra-arg2"})()
    commit_mock.assert_called_once_with(ANY, args="-- -extra-args1 -extra-arg2")
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
@pytest.mark.parametrize("editor", ["vim", None])
def test_manual_edit(editor, default_config, mocker: MockFixture, tmp_path):
    mocker.patch("commitizen.git.get_core_editor", return_value=editor)
    subprocess_mock = mocker.patch("subprocess.call")

    mocker.patch("shutil.which", return_value=editor)

    test_message = "Initial commit message"
    temp_file = tmp_path / "temp_commit_message"
    temp_file.write_text(test_message)

    mock_temp_file = mocker.patch("tempfile.NamedTemporaryFile")
    mock_temp_file.return_value.__enter__.return_value.name = str(temp_file)

    commit_cmd = commands.Commit(default_config, {"edit": True})

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
def test_commit_when_nothing_added_to_commit(default_config, mocker: MockFixture, out):
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

    commands.Commit(default_config, {})()

    commit_mock.assert_called_once()
    error_mock.assert_called_once_with(out)


@pytest.mark.usefixtures("staging_is_clean", "commit_mock")
def test_commit_command_with_config_message_length_limit(
    default_config, success_mock: MockType, prompt_mock_feat: MockType
):
    prefix = prompt_mock_feat.return_value["prefix"]
    subject = prompt_mock_feat.return_value["subject"]
    message_length = len(f"{prefix}: {subject}")

    commands.Commit(default_config, {"message_length_limit": message_length})()
    success_mock.assert_called_once()

    with pytest.raises(CommitMessageLengthExceededError):
        commands.Commit(default_config, {"message_length_limit": message_length - 1})()

    default_config.settings["message_length_limit"] = message_length
    success_mock.reset_mock()
    commands.Commit(default_config, {})()
    success_mock.assert_called_once()

    default_config.settings["message_length_limit"] = message_length - 1
    with pytest.raises(CommitMessageLengthExceededError):
        commands.Commit(default_config, {})()

    # Test default_config message length limit is overridden by CLI argument
    success_mock.reset_mock()
    commands.Commit(default_config, {"message_length_limit": message_length})()
    success_mock.assert_called_once()

    success_mock.reset_mock()
    commands.Commit(default_config, {"message_length_limit": 0})()
    success_mock.assert_called_once()
