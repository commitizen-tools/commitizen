import os
import re

import pytest

from commitizen import cmd, defaults
from commitizen.config import BaseConfig


@pytest.fixture(scope="function")
def tmp_git_project(tmpdir):
    with tmpdir.as_cwd():
        cmd.run("git init")

        yield tmpdir


@pytest.fixture(scope="function")
def tmp_commitizen_project(tmp_git_project):
    with tmp_git_project.as_cwd():
        tmp_commitizen_cfg_file = tmp_git_project.join("pyproject.toml")
        tmp_commitizen_cfg_file.write("[tool.commitizen]\n" 'version="0.1.0"\n')

        yield tmp_git_project


@pytest.fixture(scope="function")
def tmp_commitizen_project_with_gpg(tmp_commitizen_project):
    _gpg_file = tmp_commitizen_project.join("gpg_setup")
    _signer_mail = "action@github.com"
    with open(_gpg_file, "w", newline="") as f:
        f.write("Key-Type: RSA" + os.linesep)
        f.write("Key-Length: 2048" + os.linesep)
        f.write("Subkey-Type: RSA" + os.linesep)
        f.write("Subkey-Length: 2048" + os.linesep)
        f.write("Name-Real: GitHub Action" + os.linesep)
        f.write("Name-Comment: with stupid passphrase" + os.linesep)
        f.write(f"Name-Email: {_signer_mail}" + os.linesep)
        f.write("Expire-Date: 1" + os.linesep)

    cmd.run(
        f"gpg --batch --passphrase '' --pinentry-mode loopback --generate-key {_gpg_file}"
    )

    _new_key = cmd.run(f"gpg --list-secret-keys {_signer_mail}")
    _m = re.search(
        rf"[a-zA-Z0-9 \[\]-_]*{os.linesep}[ ]*([0-9A-Za-z]*){os.linesep}[{os.linesep}a-zA-Z0-9 \[\]-_<>@]*",
        _new_key.out,
    )

    if _m:
        _key_id = _m.group(1)
        cmd.run("git config --global commit.gpgsign true")
        cmd.run(f"git config --global user.signingkey {_key_id}")

    yield tmp_commitizen_project


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    return _config


@pytest.fixture()
def config_path() -> str:
    return os.path.join(os.getcwd(), "pyproject.toml")
