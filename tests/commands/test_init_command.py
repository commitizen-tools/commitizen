from __future__ import annotations

import json
import os
import sys
from typing import Any
from unittest import mock

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


PRE_COMMIT_CONFIG_FILENAME = ".pre-commit-config.yaml"
CZ_HOOK_CONFIG = {
    "repo": "https://github.com/commitizen-tools/commitizen",
    "rev": f"v{__version__}",
    "hooks": [
        {"id": "commitizen"},
        {"id": "commitizen-branch", "stages": ["push"]},
    ],
}

EXPECTED_CONFIG = (
    "[tool.commitizen]\n"
    'name = "cz_conventional_commits"\n'
    'tag_format = "$version"\n'
    'version_scheme = "semver"\n'
    "update_changelog_on_bump = true\n"
    "major_version_zero = true\n"
    'version = "0.0.1"\n'
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
            assert EXPECTED_CONFIG == toml_file.read()

        assert not os.path.isfile(PRE_COMMIT_CONFIG_FILENAME)


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
        new_callable=mock.PropertyMock,
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
            assert config_data == EXPECTED_CONFIG


def check_pre_commit_config(expected: list[dict[str, Any]]):
    """
    Check the content of pre-commit config is as expected
    """
    with open(PRE_COMMIT_CONFIG_FILENAME) as pre_commit_file:
        assert {"repos": expected} == yaml.safe_load(pre_commit_file.read())


@pytest.mark.usefixtures("pre_commit_installed")
class TestPreCommitCases:
    def test_no_existing_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            commands.Init(config)()
            check_cz_config(default_choice)
            check_pre_commit_config([CZ_HOOK_CONFIG])

    def test_empty_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            p = tmpdir.join(PRE_COMMIT_CONFIG_FILENAME)
            p.write("")

            commands.Init(config)()
            check_cz_config(default_choice)
            check_pre_commit_config([CZ_HOOK_CONFIG])

    def test_pre_commit_config_without_cz_hook(_, default_choice, tmpdir, config):
        existing_hook_config = {
            "repo": "https://github.com/pre-commit/pre-commit-hooks",
            "rev": "v1.2.3",
            "hooks": [{"id", "trailing-whitespace"}],
        }

        with tmpdir.as_cwd():
            p = tmpdir.join(PRE_COMMIT_CONFIG_FILENAME)
            p.write(yaml.safe_dump({"repos": [existing_hook_config]}))

            commands.Init(config)()
            check_cz_config(default_choice)
            check_pre_commit_config([existing_hook_config, CZ_HOOK_CONFIG])

    def test_pre_commit_config_yaml_without_repos(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            # Write a dictionary YAML content without 'repos' key
            p = tmpdir.join(PRE_COMMIT_CONFIG_FILENAME)
            p.write(
                yaml.safe_dump({"some_other_key": "value"})
            )  # Dictionary without 'repos' key

            commands.Init(config)()
            check_cz_config(default_choice)
            # Should use DEFAULT_CONFIG since the file content doesn't have 'repos' key
            check_pre_commit_config([CZ_HOOK_CONFIG])

    def test_pre_commit_config_yaml_not_a_dict(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            # Write a dictionary YAML content without 'repos' key
            p = tmpdir.join(PRE_COMMIT_CONFIG_FILENAME)
            p.write(
                yaml.safe_dump(["item1", "item2"])
            )  # Dictionary without 'repos' key

            commands.Init(config)()
            check_cz_config(default_choice)
            # Should use DEFAULT_CONFIG since the file content doesn't have 'repos' key
            check_pre_commit_config([CZ_HOOK_CONFIG])

    def test_cz_hook_exists_in_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            p = tmpdir.join(PRE_COMMIT_CONFIG_FILENAME)
            p.write(yaml.safe_dump({"repos": [CZ_HOOK_CONFIG]}))

            commands.Init(config)()
            check_cz_config(default_choice)
            # check that config is not duplicated
            check_pre_commit_config([CZ_HOOK_CONFIG])


class TestNoPreCommitInstalled:
    def test_pre_commit_not_installed(
        _, mocker: MockFixture, config, default_choice, tmpdir
    ):
        # Assume `pre-commit` is not installed
        mocker.patch(
            "commitizen.commands.init.ProjectInfo.is_pre_commit_installed",
            new_callable=mock.PropertyMock,
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
            new_callable=mock.PropertyMock,
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


def test_init_with_non_commitizen_version_provider(config, mocker: MockFixture, tmpdir):
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion("pep621"),  # Select a non-commitizen version provider
            FakeQuestion("semver"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.checkbox", return_value=FakeQuestion(None))

    with tmpdir.as_cwd():
        commands.Init(config)()
        with open("pyproject.toml", encoding="utf-8") as toml_file:
            content = toml_file.read()
            assert 'version_provider = "pep621"' in content
            assert (
                'version = "0.0.1"' not in content
            )  # Version should not be set for non-commitizen providers


class TestVersionProviderDefault:
    def test_default_for_python_poetry(self, config, mocker: MockFixture):
        mock_project_info = mocker.Mock()
        mock_project_info.is_python = True
        mock_project_info.is_python_poetry = True
        mock_project_info.is_python_uv = False
        mocker.patch(
            "commitizen.commands.init.ProjectInfo", return_value=mock_project_info
        )
        init = commands.Init(config)
        assert init.project_info.default_version_provider == "poetry"

    def test_default_for_python_uv(self, config, mocker: MockFixture):
        mock_project_info = mocker.Mock()
        mock_project_info.is_python = True
        mock_project_info.is_python_poetry = False
        mock_project_info.is_python_uv = True
        mocker.patch(
            "commitizen.commands.init.ProjectInfo", return_value=mock_project_info
        )
        init = commands.Init(config)
        assert init.project_info.default_version_provider == "uv"

    def test_default_for_python_pep621(self, config, mocker: MockFixture):
        mock_project_info = mocker.Mock()
        mock_project_info.is_python = True
        mock_project_info.is_python_poetry = False
        mock_project_info.is_python_uv = False
        mocker.patch(
            "commitizen.commands.init.ProjectInfo", return_value=mock_project_info
        )
        init = commands.Init(config)
        assert init.project_info.default_version_provider == "pep621"

    def test_default_for_rust_cargo(self, config, mocker: MockFixture):
        mock_project_info = mocker.Mock()
        mock_project_info.is_python = False
        mock_project_info.is_rust_cargo = True
        mocker.patch(
            "commitizen.commands.init.ProjectInfo", return_value=mock_project_info
        )
        init = commands.Init(config)
        assert init.project_info.default_version_provider == "cargo"

    def test_default_for_npm_package(self, config, mocker: MockFixture):
        mock_project_info = mocker.Mock()
        mock_project_info.is_python = False
        mock_project_info.is_rust_cargo = False
        mock_project_info.is_npm_package = True
        mocker.patch(
            "commitizen.commands.init.ProjectInfo", return_value=mock_project_info
        )
        init = commands.Init(config)
        assert init.project_info.default_version_provider == "npm"

    def test_default_for_php_composer(self, config, mocker: MockFixture):
        mock_project_info = mocker.Mock()
        mock_project_info.is_python = False
        mock_project_info.is_rust_cargo = False
        mock_project_info.is_npm_package = False
        mock_project_info.is_php_composer = True
        mocker.patch(
            "commitizen.commands.init.ProjectInfo", return_value=mock_project_info
        )
        init = commands.Init(config)
        assert init.project_info.default_version_provider == "composer"

    def test_default_fallback_to_commitizen(self, config, mocker: MockFixture):
        mock_project_info = mocker.Mock()
        mock_project_info.is_python = False
        mock_project_info.is_rust_cargo = False
        mock_project_info.is_npm_package = False
        mock_project_info.is_php_composer = False
        mocker.patch(
            "commitizen.commands.init.ProjectInfo", return_value=mock_project_info
        )
        init = commands.Init(config)
        assert init.project_info.default_version_provider == "commitizen"
