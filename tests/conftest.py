from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from commitizen import cmd, defaults
from commitizen.changelog_formats import (
    ChangelogFormat,
    get_changelog_format,
)
from commitizen.config import BaseConfig
from commitizen.cz import registry
from commitizen.cz.base import BaseCommitizen

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from pytest_mock import MockerFixture

    from commitizen.question import CzQuestion
    from tests.utils import UtilFixture


SIGNER = "GitHub Action"
SIGNER_MAIL = "action@github.com"
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"

pytest_plugins = [
    "tests.utils",
]


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture
def in_repo_root(repo_root: Path) -> Iterator[Path]:
    cwd = os.getcwd()
    os.chdir(repo_root)
    yield repo_root
    os.chdir(cwd)


@pytest.fixture
def data_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "data"


@pytest.fixture(scope="session")
def set_default_gitconfig() -> dict[str, str]:
    return {
        "user.name": "SIGNER",
        "user.email": SIGNER_MAIL,
        "safe.directory": "*",
        "init.defaultBranch": "master",
    }


@pytest.fixture
def chdir(tmp_path: Path) -> Iterator[Path]:
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


@pytest.fixture
def tmp_git_project(tmpdir):
    with tmpdir.as_cwd():
        cmd.run("git init")

        yield tmpdir


@pytest.fixture
def tmp_commitizen_project(tmp_git_project):
    tmp_commitizen_cfg_file = tmp_git_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write('[tool.commitizen]\nversion="0.1.0"\n')

    return tmp_git_project


@pytest.fixture
def tmp_project_root(tmp_commitizen_project) -> Path:
    return Path(tmp_commitizen_project)


@pytest.fixture
def pyproject(tmp_project_root: Path) -> Path:
    return tmp_project_root / "pyproject.toml"


@pytest.fixture
def tmp_commitizen_project_initial(tmp_git_project, util: UtilFixture):
    def _initial(
        config_extra: str | None = None,
        version="0.1.0",
        initial_commit="feat: new user interface",
    ):
        with tmp_git_project.as_cwd():
            tmp_commitizen_cfg_file = tmp_git_project.join("pyproject.toml")
            tmp_commitizen_cfg_file.write(f'[tool.commitizen]\nversion="{version}"\n')
            tmp_version_file = tmp_git_project.join("__version__.py")
            tmp_version_file.write(version)
            tmp_commitizen_cfg_file = tmp_git_project.join("pyproject.toml")
            tmp_version_file_string = str(tmp_version_file).replace("\\", "/")
            tmp_commitizen_cfg_file.write(
                f"{tmp_commitizen_cfg_file.read()}\n"
                f'version_files = ["{tmp_version_file_string}"]\n'
            )
            if config_extra:
                tmp_commitizen_cfg_file.write(config_extra, mode="a")
            util.create_file_and_commit(initial_commit)

            return tmp_git_project

    return _initial


def _get_gpg_keyid(signer_mail):
    _new_key = cmd.run(f"gpg --list-secret-keys {signer_mail}")
    _m = re.search(
        r"[a-zA-Z0-9 \[\]-_]*\n[ ]*([0-9A-Za-z]*)\n[\na-zA-Z0-9 \[\]-_<>@]*",
        _new_key.out,
    )
    return _m.group(1) if _m else None


@pytest.fixture
def tmp_commitizen_project_with_gpg(tmp_commitizen_project):
    # create a temporary GPGHOME to store a temporary keyring.
    # Home path must be less than 104 characters
    gpg_home = tempfile.TemporaryDirectory(suffix="_cz")
    old_gnupghome = os.environ.get("GNUPGHOME")
    if os.name != "nt":
        os.environ["GNUPGHOME"] = gpg_home.name  # tempdir = temp keyring

    try:
        # create a key (a keyring will be generated within GPUPGHOME)
        subprocess.run(
            [
                "gpg",
                "--batch",
                "--yes",
                "--debug-quick-random",
                "--passphrase",
                "",
                "--quick-gen-key",
                f"{SIGNER} {SIGNER_MAIL}",
            ],
            check=True,
        )
        key_id = _get_gpg_keyid(SIGNER_MAIL)
        assert key_id

        # configure git to use gpg signing
        cmd.run("git config commit.gpgsign true")
        cmd.run(f"git config user.signingkey {key_id}")

        yield tmp_commitizen_project
    finally:
        if old_gnupghome is not None:
            os.environ["GNUPGHOME"] = old_gnupghome
        elif "GNUPGHOME" in os.environ and os.name != "nt":
            os.environ.pop("GNUPGHOME")
        gpg_home.cleanup()


@pytest.fixture
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    return _config


class SemverCommitizen(BaseCommitizen):
    """A minimal cz rules used to test changelog and bump.

    Samples:
    ```
    minor(users): add email to user
    major: removed user profile
    patch(deps): updated dependency for security
    ```
    """

    bump_pattern = r"^(patch|minor|major)"
    bump_map = {
        "major": "MAJOR",
        "minor": "MINOR",
        "patch": "PATCH",
    }
    bump_map_major_version_zero = {
        "major": "MINOR",
        "minor": "MINOR",
        "patch": "PATCH",
    }
    changelog_pattern = r"^(patch|minor|major)"
    commit_parser = r"^(?P<change_type>patch|minor|major)(?:\((?P<scope>[^()\r\n]*)\)|\()?:?\s(?P<message>.+)"
    change_type_map = {
        "major": "Breaking Changes",
        "minor": "Features",
        "patch": "Bugs",
    }

    def questions(self) -> list[CzQuestion]:
        return [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "patch",
                        "name": "patch: a bug fix",
                        "key": "p",
                    },
                    {
                        "value": "minor",
                        "name": "minor: a new feature, non-breaking",
                        "key": "m",
                    },
                    {
                        "value": "major",
                        "name": "major: a breaking change",
                        "key": "b",
                    },
                ],
            },
            {
                "type": "input",
                "name": "subject",
                "message": (
                    "Write a short and imperative summary of the code changes: (lower case and no period)\n"
                ),
            },
        ]

    def message(self, answers: Mapping) -> str:
        prefix = answers["prefix"]
        subject = answers.get("subject", "default message").trim()
        return f"{prefix}: {subject}"

    def example(self) -> str:
        return ""

    def schema(self) -> str:
        return ""

    def schema_pattern(self) -> str:
        return ""

    def info(self) -> str:
        return ""


@pytest.fixture
def use_cz_semver(mocker):
    new_cz = {**registry, "cz_semver": SemverCommitizen}
    mocker.patch.dict("commitizen.cz.registry", new_cz)


class MockPlugin(BaseCommitizen):
    def questions(self) -> list[CzQuestion]:
        return []

    def message(self, answers: Mapping) -> str:
        return ""

    def example(self) -> str:
        return ""

    def schema(self) -> str:
        return ""

    def schema_pattern(self) -> str:
        return ""

    def info(self) -> str:
        return ""


@pytest.fixture
def mock_plugin(mocker: MockerFixture, config: BaseConfig) -> BaseCommitizen:
    mock = MockPlugin(config)
    mocker.patch("commitizen.factory.committer_factory", return_value=mock)
    return mock


SUPPORTED_FORMATS = ("markdown", "textile", "asciidoc", "restructuredtext")


@pytest.fixture(params=SUPPORTED_FORMATS)
def changelog_format(
    config: BaseConfig, request: pytest.FixtureRequest
) -> ChangelogFormat:
    """For tests relying on formats specifics"""
    format: str = request.param
    config.settings["changelog_format"] = format
    if "tmp_commitizen_project" in request.fixturenames:
        tmp_commitizen_project = request.getfixturevalue("tmp_commitizen_project")
        pyproject = tmp_commitizen_project / "pyproject.toml"
        pyproject.write(f'{pyproject.read()}\nchangelog_format = "{format}"\n')
    return get_changelog_format(config)


@pytest.fixture
def any_changelog_format(config: BaseConfig) -> ChangelogFormat:
    """For test not relying on formats specifics, use the default"""
    config.settings["changelog_format"] = defaults.CHANGELOG_FORMAT
    return get_changelog_format(config)


@pytest.fixture(params=[pytest.param(PYTHON_VERSION, id=f"py_{PYTHON_VERSION}")])
def python_version(request: pytest.FixtureRequest) -> str:
    """The current python version in '{major}.{minor}' format"""
    return cast("str", request.param)


@pytest.fixture
def consistent_terminal_output(monkeypatch: pytest.MonkeyPatch):
    """Force consistent terminal output."""
    monkeypatch.setenv("COLUMNS", "80")
    monkeypatch.setenv("TERM", "dumb")
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.setenv("LANG", "C")
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("PAGER", "cat")
