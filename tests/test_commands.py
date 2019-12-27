import contextlib
import os
import shutil
import tempfile
from unittest import mock

import pytest

from commitizen import cmd, commands, defaults
from commitizen.cz.exceptions import CzException
from commitizen.config import BaseConfig
from commitizen.__version__ import __version__


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.name})
    return _config


@pytest.fixture
def staging_is_clean(mocker):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = False


@contextlib.contextmanager
def get_temp_dir():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit(config, mocker):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "")
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {})()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_fails_no_backup(config, mocker):
    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "")

    with pytest.raises(SystemExit):
        commands.Commit(config, {"retry": True})()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_works(config, mocker):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #21",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("", "error", "", "")
    error_mock = mocker.patch("commitizen.out.error")

    with pytest.raises(SystemExit):
        commit_cmd = commands.Commit(config, {})
        temp_file = commit_cmd.temp_file
        commit_cmd()

    prompt_mock.assert_called_once()
    error_mock.assert_called_once()
    assert os.path.isfile(temp_file)

    # Previous commit failed, so retry should pick up the backup commit
    # commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "")
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {"retry": True})()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21")
    prompt_mock.assert_called_once()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_dry_run_option(config, mocker):
    prompt_mock = mocker = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #57",
        "footer": "",
    }

    with pytest.raises(SystemExit):
        commit_cmd = commands.Commit(config, {"dry_run": True})
        commit_cmd()


def test_commit_when_nothing_to_commit(config, mocker):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = True

    with pytest.raises(SystemExit) as err:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    assert err.value.code == commands.commit.NOTHING_TO_COMMIT


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_customized_expected_raised(config, mocker, capsys):
    _err = ValueError()
    _err.__context__ = CzException("This is the root custom err")
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.side_effect = _err

    with pytest.raises(SystemExit) as err:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    assert err.value.code == commands.commit.CUSTOM_ERROR

    # Assert only the content in the formatted text
    captured = capsys.readouterr()
    assert "This is the root custom err" in captured.err


def test_example(config):
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Example(config)()
        write_mock.assert_called_once()


def test_info(config):
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Info(config)()
        write_mock.assert_called_once()


def test_schema(config):
    with mock.patch("commitizen.out.write") as write_mock:
        commands.Schema(config)()
        write_mock.assert_called_once()


def test_list_cz(config):
    with mock.patch("commitizen.out.write") as mocked_write:
        commands.ListCz(config)()
        mocked_write.assert_called_once()


def test_version_for_showing_project_version(config, capsys):
    # No version exist
    commands.Version(config, {"project": True, "commitizen": False})()
    captured = capsys.readouterr()
    assert "No project information in this project." in captured.err

    config.settings["version"] = "v0.0.1"
    commands.Version(config, {"project": True, "commitizen": False})()
    captured = capsys.readouterr()
    assert "Project Version: v0.0.1" in captured.out


def test_version_for_showing_commitizen_version(config, capsys):
    commands.Version(config, {"project": False, "commitizen": True})()
    captured = capsys.readouterr()
    assert f"Installed Commitizen Version: {__version__}" in captured.out


def test_check_no_conventional_commit(config, mocker):
    with pytest.raises(SystemExit):
        error_mock = mocker.patch("commitizen.out.error")

        with get_temp_dir() as dir:

            tempfile = os.path.join(dir, "temp_commit_file")
            with open(tempfile, "w") as f:
                f.write("no conventional commit")

            check_cmd = commands.Check(
                config=config, arguments={"commit_msg_file": tempfile}
            )
            check_cmd()
            error_mock.assert_called_once()


def test_check_conventional_commit(config, mocker):
    success_mock = mocker.patch("commitizen.out.success")
    with get_temp_dir() as dir:

        tempfile = os.path.join(dir, "temp_commit_file")
        with open(tempfile, "w") as f:
            f.write("feat(lang): added polish language")

        check_cmd = commands.Check(
            config=config, arguments={"commit_msg_file": tempfile}
        )

        check_cmd()
        success_mock.assert_called_once()


def test_check_command_when_commit_file_not_found(config):
    with pytest.raises(FileNotFoundError):
        commands.Check(config=config, arguments={"commit_msg_file": ""})()


def test_init_when_config_already_exists(config, capsys):
    # Set config path
    path = "tests/pyproject.toml"
    config.add_path(path)

    commands.Init(config)()
    captured = capsys.readouterr()
    assert captured.out == f"Config file {path} already exists\n"
