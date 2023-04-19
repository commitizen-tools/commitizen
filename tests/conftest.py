import os
import re
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from commitizen import cmd, defaults
from commitizen.config import BaseConfig
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
        config_extra: Optional[str] = None,
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
