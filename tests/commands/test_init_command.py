from __future__ import annotations

import json
import os
import sys
from typing import Any

import pytest
import yaml
from pytest_mock import MockFixture

from commitizen import cli, commands
from commitizen.__version__ import __version__
from commitizen.exceptions import InitFailedError, NoAnswersError
from tests.utils import skip_below_py_3_10


class FakeQuestion:
    def __init__(self, expected_return):
        self.expected_return = expected_return

    def ask(self):
        return self.expected_return

    def unsafe_ask(self):
        return self.expected_return


pre_commit_config_filename = ".pre-commit-config.yaml"
cz_hook_config = {
    "repo": "https://github.com/commitizen-tools/commitizen",
    "rev": f"v{__version__}",
    "hooks": [
        {"id": "commitizen"},
        {"id": "commitizen-branch", "stages": ["pre-push"]},
    ],
}

expected_config = (
    "[tool.commitizen]\n"
    'name = "cz_conventional_commits"\n'
    'tag_format = "$version"\n'
    'version_scheme = "semver"\n'
    'version = "0.0.1"\n'
    "update_changelog_on_bump = true\n"
    "major_version_zero = true\n"
)

EXPECTED_DICT_CONFIG = {
    "commitizen": {
        "name": "cz_conventional_commits",
        "tag_format": "$version",
        "version_scheme": "semver",
        "version": "0.0.1",
        "update_changelog_on_bump": True,
        "major_version_zero": True,
    }
}


def test_init_without_setup_pre_commit_hook(tmpdir, mocker: MockFixture, config):
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    # Return None to skip hook installation
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()

        with open("pyproject.toml", encoding="utf-8") as toml_file:
            config_data = toml_file.read()
        assert config_data == expected_config

        assert not os.path.isfile(pre_commit_config_filename)


def test_init_when_config_already_exists(config, capsys):
    # Set config path
    path = os.sep.join(["tests", "pyproject.toml"])
    config.path = path

    commands.Init(config)()
    captured = capsys.readouterr()
    assert captured.out == f"Config file {path} already exists\n"


def test_init_without_choosing_tag(config, mocker: MockFixture, tmpdir):
    mocker.patch(
        "commitizen.commands.init.get_tag_names", return_value=["0.0.2", "0.0.1"]
    )
    mocker.patch("commitizen.commands.init.get_latest_tag_name", return_value="0.0.2")
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion(""),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(False))
    mocker.patch("questionary.text", return_value=FakeQuestion("y"))

    with tmpdir.as_cwd():
        with pytest.raises(NoAnswersError):
            commands.Init(config)()


def test_executed_pre_commit_command(config):
    init = commands.Init(config)
    expected_cmd = "pre-commit install --hook-type commit-msg --hook-type pre-push"
    assert init._gen_pre_commit_cmd(["commit-msg", "pre-push"]) == expected_cmd


@pytest.fixture(scope="function")
def pre_commit_installed(mocker: MockFixture):
    # Assume the `pre-commit` is installed
    mocker.patch(
        "commitizen.commands.init.ProjectInfo.is_pre_commit_installed",
        return_value=True,
    )
    # And installation success (i.e. no exception raised)
    mocker.patch(
        "commitizen.commands.init.Init._exec_install_pre_commit_hook",
        return_value=None,
    )


@pytest.fixture(scope="function", params=["pyproject.toml", ".cz.json", ".cz.yaml"])
def default_choice(request, mocker: MockFixture):
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion(request.param),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch(
        "questionary.checkbox",
        return_value=FakeQuestion(["commit-msg", "pre-push"]),
    )
    yield request.param


def check_cz_config(config: str):
    """
    Check the content of commitizen config is as expected

    Args:
        config: The config path
    """
    with open(config) as file:
        if "json" in config:
            assert json.load(file) == EXPECTED_DICT_CONFIG
        elif "yaml" in config:
            assert yaml.load(file, Loader=yaml.FullLoader) == EXPECTED_DICT_CONFIG
        else:
            config_data = file.read()
            assert config_data == expected_config


def check_pre_commit_config(expected: list[dict[str, Any]]):
    """
    Check the content of pre-commit config is as expected
    """
    with open(pre_commit_config_filename) as pre_commit_file:
        pre_commit_config_data = yaml.safe_load(pre_commit_file.read())
    assert pre_commit_config_data == {"repos": expected}


@pytest.mark.usefixtures("pre_commit_installed")
class TestPreCommitCases:
    def test_no_existing_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            commands.Init(config)()
            check_cz_config(default_choice)
            check_pre_commit_config([cz_hook_config])

    def test_empty_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            p = tmpdir.join(pre_commit_config_filename)
            p.write("")

            commands.Init(config)()
            check_cz_config(default_choice)
            check_pre_commit_config([cz_hook_config])

    def test_pre_commit_config_without_cz_hook(_, default_choice, tmpdir, config):
        existing_hook_config = {
            "repo": "https://github.com/pre-commit/pre-commit-hooks",
            "rev": "v1.2.3",
            "hooks": [{"id", "trailing-whitespace"}],
        }

        with tmpdir.as_cwd():
            p = tmpdir.join(pre_commit_config_filename)
            p.write(yaml.safe_dump({"repos": [existing_hook_config]}))

            commands.Init(config)()
            check_cz_config(default_choice)
            check_pre_commit_config([existing_hook_config, cz_hook_config])

    def test_cz_hook_exists_in_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            p = tmpdir.join(pre_commit_config_filename)
            p.write(yaml.safe_dump({"repos": [cz_hook_config]}))

            commands.Init(config)()
            check_cz_config(default_choice)
            # check that config is not duplicated
            check_pre_commit_config([cz_hook_config])


class TestNoPreCommitInstalled:
    def test_pre_commit_not_installed(
        _, mocker: MockFixture, config, default_choice, tmpdir
    ):
        # Assume `pre-commit` is not installed
        mocker.patch(
            "commitizen.commands.init.ProjectInfo.is_pre_commit_installed",
            return_value=False,
        )
        with tmpdir.as_cwd():
            with pytest.raises(InitFailedError):
                commands.Init(config)()

    def test_pre_commit_exec_failed(
        _, mocker: MockFixture, config, default_choice, tmpdir
    ):
        # Assume `pre-commit` is installed
        mocker.patch(
            "commitizen.commands.init.ProjectInfo.is_pre_commit_installed",
            return_value=True,
        )
        # But pre-commit installation will fail
        mocker.patch(
            "commitizen.commands.init.Init._exec_install_pre_commit_hook",
            side_effect=InitFailedError("Mock init failed error."),
        )
        with tmpdir.as_cwd():
            with pytest.raises(InitFailedError):
                commands.Init(config)()


class TestAskTagFormat:
    def test_confirm_v_tag_format(self, mocker: MockFixture, config):
        init = commands.Init(config)
        mocker.patch("questionary.confirm", return_value=FakeQuestion(True))

        result = init._ask_tag_format("v1.0.0")
        assert result == r"v$version"

    def test_reject_v_tag_format(self, mocker: MockFixture, config):
        init = commands.Init(config)
        mocker.patch("questionary.confirm", return_value=FakeQuestion(False))
        mocker.patch("questionary.text", return_value=FakeQuestion("custom-$version"))

        result = init._ask_tag_format("v1.0.0")
        assert result == "custom-$version"

    def test_non_v_tag_format(self, mocker: MockFixture, config):
        init = commands.Init(config)
        mocker.patch("questionary.text", return_value=FakeQuestion("custom-$version"))

        result = init._ask_tag_format("1.0.0")
        assert result == "custom-$version"

    def test_empty_input_returns_default(self, mocker: MockFixture, config):
        init = commands.Init(config)
        mocker.patch("questionary.confirm", return_value=FakeQuestion(False))
        mocker.patch("questionary.text", return_value=FakeQuestion(""))

        result = init._ask_tag_format("v1.0.0")
        assert result == "$version"  # This is the default format from DEFAULT_SETTINGS


@skip_below_py_3_10
def test_init_command_shows_description_when_use_help_option(
    mocker: MockFixture, capsys, file_regression
):
    testargs = ["cz", "init", "--help"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    file_regression.check(out, extension=".txt")


def test_init_with_confirmed_tag_format(config, mocker: MockFixture, tmpdir):
    mocker.patch(
        "commitizen.commands.init.get_tag_names", return_value=["v0.0.2", "v0.0.1"]
    )
    mocker.patch("commitizen.commands.init.get_latest_tag_name", return_value="v0.0.2")
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()
        with open("pyproject.toml", encoding="utf-8") as toml_file:
            assert 'tag_format = "v$version"' in toml_file.read()


def test_init_with_no_existing_tags(config, mocker: MockFixture, tmpdir):
    mocker.patch("commitizen.commands.init.get_tag_names", return_value=[])
    mocker.patch("commitizen.commands.init.get_latest_tag_name", return_value="v1.0.0")
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(False))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()
        with open("pyproject.toml", encoding="utf-8") as toml_file:
            assert 'version = "0.0.1"' in toml_file.read()


def test_init_with_no_existing_latest_tag(config, mocker: MockFixture, tmpdir):
    mocker.patch("commitizen.commands.init.get_latest_tag_name", return_value=None)
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()
        with open("pyproject.toml", encoding="utf-8") as toml_file:
            assert 'version = "0.0.1"' in toml_file.read()


def test_init_with_existing_tags(config, mocker: MockFixture, tmpdir):
    expected_tags = ["v1.0.0", "v0.9.0", "v0.8.0"]
    mocker.patch("commitizen.commands.init.get_tag_names", return_value=expected_tags)
    mocker.patch("commitizen.commands.init.get_latest_tag_name", return_value="v1.0.0")
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion("semver"),  # Select version scheme first
            FakeQuestion("v1.0.0"),  # Then select the latest tag
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()
        with open("pyproject.toml", encoding="utf-8") as toml_file:
            assert 'version = "1.0.0"' in toml_file.read()


def test_init_with_valid_tag_selection(config, mocker: MockFixture, tmpdir):
    expected_tags = ["v1.0.0", "v0.9.0", "v0.8.0"]
    mocker.patch("commitizen.commands.init.get_tag_names", return_value=expected_tags)
    mocker.patch("commitizen.commands.init.get_latest_tag_name", return_value="v1.0.0")

    # Mock all questionary.select calls in the exact order they appear in Init.__call__
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),  # _ask_config_path
            FakeQuestion("cz_conventional_commits"),  # _ask_name
            FakeQuestion("commitizen"),  # _ask_version_provider
            FakeQuestion("v0.9.0"),  # _ask_tag (after confirm=False)
            FakeQuestion("semver"),  # _ask_version_scheme
        ],
    )

    mocker.patch(
        "questionary.confirm", return_value=FakeQuestion(False)
    )  # Don't confirm latest tag
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()
        with open("pyproject.toml", encoding="utf-8") as toml_file:
            content = toml_file.read()
            assert 'version = "0.9.0"' in content
            assert 'version_scheme = "semver"' in content


def test_init_configuration_settings(tmpdir, mocker: MockFixture, config):
    """Test that all configuration settings are properly initialized."""
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("commitizen"),
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()

        with open("pyproject.toml", encoding="utf-8") as toml_file:
            config_data = toml_file.read()

        # Verify all expected settings are present
        assert 'name = "cz_conventional_commits"' in config_data
        assert 'tag_format = "$version"' in config_data
        assert 'version_scheme = "semver"' in config_data
        assert 'version = "0.0.1"' in config_data
        assert "update_changelog_on_bump = true" in config_data
        assert "major_version_zero = true" in config_data


def test_init_configuration_with_version_provider(tmpdir, mocker: MockFixture, config):
    """Test configuration initialization with a different version provider."""
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("pep621"),  # Different version provider
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()

        with open("pyproject.toml", encoding="utf-8") as toml_file:
            config_data = toml_file.read()

        # Verify version provider is set instead of version
        assert 'name = "cz_conventional_commits"' in config_data
        assert 'tag_format = "$version"' in config_data
        assert 'version_scheme = "semver"' in config_data
        assert 'version_provider = "pep621"' in config_data
        assert "update_changelog_on_bump = true" in config_data
        assert "major_version_zero = true" in config_data
        assert (
            "version = " not in config_data
        )  # Version should not be set when using version_provider
