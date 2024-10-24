from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Iterator

import pytest
from pytest_mock import MockerFixture

from commitizen import cmd, defaults, git
from commitizen.changelog_formats import (
    ChangelogFormat,
    get_changelog_format,
)
from commitizen.config import BaseConfig
from commitizen.cz import registry
from commitizen.cz.base import BaseCommitizen
from tests.utils import create_file_and_commit

SIGNER = "GitHub Action"
SIGNER_MAIL = "action@github.com"


@pytest.fixture(autouse=True)
def git_sandbox(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Ensure git commands are executed without the current user settings"""
    # Clear any GIT_ prefixed environment variable
    for var in os.environ:
        if var.startswith("GIT_"):
            monkeypatch.delenv(var)

    # Define a dedicated temporary git config
    gitconfig = tmp_path / ".git" / "config"
    if not gitconfig.parent.exists():
        gitconfig.parent.mkdir()
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(gitconfig))
    r = cmd.run(f"git config --file {gitconfig} user.name {SIGNER}")
    assert r.return_code == 0, r.err
    r = cmd.run(f"git config --file {gitconfig} user.email {SIGNER_MAIL}")
    assert r.return_code == 0, r.err
    cmd.run("git config --global init.defaultBranch master")


@pytest.fixture
def chdir(tmp_path: Path) -> Iterator[Path]:
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


@pytest.fixture(scope="function")
def tmp_git_project(tmpdir):
    with tmpdir.as_cwd():
        cmd.run("git init")

        yield tmpdir


@pytest.fixture(scope="function")
def tmp_commitizen_project(tmp_git_project):
    tmp_commitizen_cfg_file = tmp_git_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write("[tool.commitizen]\n" 'version="0.1.0"\n')

    yield tmp_git_project


@pytest.fixture(scope="function")
def tmp_commitizen_project_initial(tmp_git_project):
    def _initial(
        config_extra: str | None = None,
        version="0.1.0",
        initial_commit="feat: new user interface",
    ):
        with tmp_git_project.as_cwd():
            tmp_commitizen_cfg_file = tmp_git_project.join("pyproject.toml")
            tmp_commitizen_cfg_file.write(
                f"[tool.commitizen]\n" f'version="{version}"\n'
            )
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
            create_file_and_commit(initial_commit)

            return tmp_git_project

    yield _initial


def _get_gpg_keyid(signer_mail):
    _new_key = cmd.run(f"gpg --list-secret-keys {signer_mail}")
    _m = re.search(
        r"[a-zA-Z0-9 \[\]-_]*\n[ ]*([0-9A-Za-z]*)\n[\na-zA-Z0-9 \[\]-_<>@]*",
        _new_key.out,
    )
    return _m.group(1) if _m else None


@pytest.fixture(scope="function")
def tmp_commitizen_project_with_gpg(tmp_commitizen_project):
    # create a temporary GPGHOME to store a temporary keyring.
    # Home path must be less than 104 characters
    gpg_home = tempfile.TemporaryDirectory(suffix="_cz")
    if os.name != "nt":
        os.environ["GNUPGHOME"] = gpg_home.name  # tempdir = temp keyring

    # create a key (a keyring will be generated within GPUPGHOME)
    c = cmd.run(
        f"gpg --batch --yes --debug-quick-random --passphrase '' --quick-gen-key '{SIGNER} {SIGNER_MAIL}'"
    )
    if c.return_code != 0:
        raise Exception(f"gpg keygen failed with err: '{c.err}'")
    key_id = _get_gpg_keyid(SIGNER_MAIL)
    assert key_id

    # configure git to use gpg signing
    cmd.run("git config commit.gpgsign true")
    cmd.run(f"git config user.signingkey {key_id}")

    yield tmp_commitizen_project


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    return _config


@pytest.fixture()
def config_path() -> str:
    return os.path.join(os.getcwd(), "pyproject.toml")


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
    commit_parser = r"^(?P<change_type>patch|minor|major)(?:\((?P<scope>[^()\r\n]*)\)|\()?:?\s(?P<message>.+)"  # noqa
    change_type_map = {
        "major": "Breaking Changes",
        "minor": "Features",
        "patch": "Bugs",
    }

    def questions(self) -> list:
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

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        subject = answers.get("subject", "default message").trim()
        return f"{prefix}: {subject}"


@pytest.fixture()
def use_cz_semver(mocker):
    new_cz = {**registry, "cz_semver": SemverCommitizen}
    mocker.patch.dict("commitizen.cz.registry", new_cz)


class MockPlugin(BaseCommitizen):
    def questions(self) -> defaults.Questions:
        return []

    def message(self, answers: dict) -> str:
        return ""


@pytest.fixture
def mock_plugin(mocker: MockerFixture, config: BaseConfig) -> BaseCommitizen:
    mock = MockPlugin(config)
    mocker.patch("commitizen.factory.commiter_factory", return_value=mock)
    return mock


class ValidationCz(BaseCommitizen):
    def questions(self):
        return [
            {"type": "input", "name": "commit", "message": "Initial commit:\n"},
            {"type": "input", "name": "issue_nb", "message": "ABC-123"},
        ]

    def message(self, answers: dict):
        return f"{answers['issue_nb']}: {answers['commit']}"

    def schema(self):
        return "<issue_nb>: <commit>"

    def schema_pattern(self):
        return r"^(?P<issue_nb>[A-Z]{3}-\d+): (?P<commit>.*)$"

    def validate_commit_message(
        self,
        commit_msg: str,
        pattern: str | None,
        allow_abort: bool,
        allowed_prefixes: list[str],
        max_msg_length: int,
    ) -> tuple[bool, list]:
        """Validate commit message against the pattern."""
        if not commit_msg:
            return allow_abort, [] if allow_abort else ["commit message is empty"]

        if pattern is None:
            return True, []

        if any(map(commit_msg.startswith, allowed_prefixes)):
            return True, []
        if max_msg_length:
            msg_len = len(commit_msg.partition("\n")[0].strip())
            if msg_len > max_msg_length:
                return False, [
                    f"commit message is too long. Max length is {max_msg_length}"
                ]
        pattern_match = bool(re.match(pattern, commit_msg))
        if not pattern_match:
            return False, [f"commit message does not match pattern {pattern}"]
        return True, []

    def format_exception_message(
        self, ill_formated_commits: list[tuple[git.GitCommit, list]]
    ) -> str:
        """Format commit errors."""
        displayed_msgs_content = "\n".join(
            [
                (
                    f'commit "{commit.rev}": "{commit.message}"\n'
                    f"errors:\n"
                    "\n".join(f"- {error}" for error in errors)
                )
                for (commit, errors) in ill_formated_commits
            ]
        )
        return (
            "commit validation: failed!\n"
            "please enter a commit message in the commitizen format.\n"
            f"{displayed_msgs_content}\n"
            f"pattern: {self.schema_pattern}"
        )


@pytest.fixture
def use_cz_custom_validator(mocker):
    new_cz = {**registry, "cz_custom_validator": ValidationCz}
    mocker.patch.dict("commitizen.cz.registry", new_cz)


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
        pyproject.write(f"{pyproject.read()}\n" f'changelog_format = "{format}"\n')
    return get_changelog_format(config)


@pytest.fixture
def any_changelog_format(config: BaseConfig) -> ChangelogFormat:
    """For test not relying on formats specifics, use the default"""
    config.settings["changelog_format"] = defaults.CHANGELOG_FORMAT
    return get_changelog_format(config)
