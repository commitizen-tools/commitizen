import json
import os

import pytest
import yaml
from pytest_mock import MockFixture

from commitizen import commands
from commitizen.__version__ import __version__
from commitizen.exceptions import InitFailedError, NoAnswersError


class FakeQuestion:
    def __init__(self, expected_return):
        self.expected_return = expected_return

    def ask(self):
        return self.expected_return


pre_commit_config_filename = ".pre-commit-config.yaml"
cz_hook_config = {
    "repo": "https://github.com/commitizen-tools/commitizen",
    "rev": f"v{__version__}",
    "hooks": [{"id": "commitizen"}],
}

expected_config = (
    "[tool.commitizen]\n"
    'name = "cz_conventional_commits"\n'
    'version = "0.0.1"\n'
    'tag_format = "$version"\n'
)

EXPECTED_DICT_CONFIG = {
    "commitizen": {
        "name": "cz_conventional_commits",
        "version": "0.0.1",
        "tag_format": "$version",
    }
}


def test_init_without_setup_pre_commit_hook(tmpdir, mocker: MockFixture, config):
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    mocker.patch("questionary.confirm", return_value=FakeQuestion(False))

    with tmpdir.as_cwd():
        commands.Init(config)()

        with open("pyproject.toml", "r") as toml_file:
            config_data = toml_file.read()
        assert config_data == expected_config

        assert not os.path.isfile(pre_commit_config_filename)


def test_init_when_config_already_exists(config, capsys):
    # Set config path
    path = os.sep.join(["tests", "pyproject.toml"])
    config.add_path(path)

    commands.Init(config)()
    captured = capsys.readouterr()
    assert captured.out == f"Config file {path} already exists\n"


def test_init_without_choosing_tag(config, mocker: MockFixture, tmpdir):
    mocker.patch(
        "commitizen.commands.init.get_tag_names", return_value=["0.0.1", "0.0.2"]
    )
    mocker.patch("commitizen.commands.init.get_latest_tag_name", return_value="0.0.2")
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
            FakeQuestion(""),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(False))
    mocker.patch("questionary.text", return_value=FakeQuestion("y"))

    with tmpdir.as_cwd():
        with pytest.raises(NoAnswersError):
            commands.Init(config)()


@pytest.fixture(scope="function")
def pre_commit_installed(mocker: MockFixture):
    # Assume the `pre-commit` is installed
    mocker.patch(
        "commitizen.commands.init.Init._search_pre_commit",
        return_value=True,
    )
    mocker.patch(
        "commitizen.commands.init.Init._exec_install_pre_commit_hook",
        return_value=True,
    )


@pytest.fixture(scope="function", params=["pyproject.toml", ".cz.json", ".cz.yaml"])
def default_choice(request, mocker: MockFixture):
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion(request.param),
            FakeQuestion("cz_conventional_commits"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion(True))
    mocker.patch("questionary.text", return_value=FakeQuestion("$version"))
    yield request.param


@pytest.mark.usefixtures("pre_commit_installed")
class TestPreCommitCases:
    def test_no_existing_pre_commit_conifg(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            commands.Init(config)()

            with open(default_choice, "r") as file:
                if "json" in default_choice:
                    assert json.load(file) == EXPECTED_DICT_CONFIG
                elif "yaml" in default_choice:
                    assert (
                        yaml.load(file, Loader=yaml.FullLoader) == EXPECTED_DICT_CONFIG
                    )
                else:
                    config_data = file.read()
                    assert config_data == expected_config

            with open(pre_commit_config_filename, "r") as pre_commit_file:
                pre_commit_config_data = yaml.safe_load(pre_commit_file.read())
            assert pre_commit_config_data == {"repos": [cz_hook_config]}

    def test_empty_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            p = tmpdir.join(pre_commit_config_filename)
            p.write("")

            commands.Init(config)()

            with open(default_choice, "r") as file:
                if "json" in default_choice:
                    assert json.load(file) == EXPECTED_DICT_CONFIG
                elif "yaml" in default_choice:
                    assert (
                        yaml.load(file, Loader=yaml.FullLoader) == EXPECTED_DICT_CONFIG
                    )
                else:
                    config_data = file.read()
                    assert config_data == expected_config

            with open(pre_commit_config_filename, "r") as pre_commit_file:
                pre_commit_config_data = yaml.safe_load(pre_commit_file.read())
            assert pre_commit_config_data == {"repos": [cz_hook_config]}

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

            with open(default_choice, "r") as file:
                if "json" in default_choice:
                    assert json.load(file) == EXPECTED_DICT_CONFIG
                elif "yaml" in default_choice:
                    assert (
                        yaml.load(file, Loader=yaml.FullLoader) == EXPECTED_DICT_CONFIG
                    )
                else:
                    config_data = file.read()
                    assert config_data == expected_config

            with open(pre_commit_config_filename, "r") as pre_commit_file:
                pre_commit_config_data = yaml.safe_load(pre_commit_file.read())
            assert pre_commit_config_data == {
                "repos": [existing_hook_config, cz_hook_config]
            }

    def test_cz_hook_exists_in_pre_commit_config(_, default_choice, tmpdir, config):
        with tmpdir.as_cwd():
            p = tmpdir.join(pre_commit_config_filename)
            p.write(yaml.safe_dump({"repos": [cz_hook_config]}))

            commands.Init(config)()

            with open(default_choice, "r") as file:
                if "json" in default_choice:
                    assert json.load(file) == EXPECTED_DICT_CONFIG
                elif "yaml" in default_choice:
                    assert (
                        yaml.load(file, Loader=yaml.FullLoader) == EXPECTED_DICT_CONFIG
                    )
                else:
                    config_data = file.read()
                    assert config_data == expected_config

            with open(pre_commit_config_filename, "r") as pre_commit_file:
                pre_commit_config_data = yaml.safe_load(pre_commit_file.read())

            # check that config is not duplicated
            assert pre_commit_config_data == {"repos": [cz_hook_config]}


class TestNoPreCommitInstalled:
    def test_pre_commit_not_installed(
        _, mocker: MockFixture, config, default_choice, tmpdir
    ):
        # Assume `pre-commit` is not installed
        mocker.patch(
            "commitizen.commands.init.Init._search_pre_commit",
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
            "commitizen.commands.init.Init._search_pre_commit",
            return_value=True,
        )
        # But pre-commit installation will fail
        mocker.patch(
            "commitizen.commands.init.Init._exec_install_pre_commit_hook",
            return_value=False,
        )
        with tmpdir.as_cwd():
            with pytest.raises(InitFailedError):
                commands.Init(config)()
