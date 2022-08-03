import os
import re
import tempfile

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


def _get_gpg_keyid(signer_mail):
    _new_key = cmd.run(f"gpg --list-secret-keys {signer_mail}")
    _m = re.search(
        rf"[a-zA-Z0-9 \[\]-_]*{os.linesep}[ ]*([0-9A-Za-z]*){os.linesep}[{os.linesep}a-zA-Z0-9 \[\]-_<>@]*",
        _new_key.out,
    )
    return _m.group(1) if _m else None


@pytest.fixture(scope="function")
def tmp_commitizen_project_with_gpg(tmp_commitizen_project):
    signer = "GitHub Action"
    signer_mail = "action@github.com"

    # create a temporary GPGHOME to store a temporary keyring.
    # Home path must be less than 104 characters
    gpg_home = tempfile.TemporaryDirectory(suffix="_cz")
    os.environ["GNUPGHOME"] = gpg_home.name  # tempdir = temp keyring

    # create a key (a keyring will be generated within GPUPGHOME)
    c = cmd.run(
        f"gpg --batch --yes --debug-quick-random --passphrase '' --quick-gen-key '{signer} {signer_mail}'"
    )
    if c.return_code != 0:
        raise Exception(f"gpg keygen failed with err: '{c.err}'")
    key_id = _get_gpg_keyid(signer_mail)
    assert key_id

    # configure git
    cmd.run("git config commit.gpgsign true")
    cmd.run(f"git config user.name {signer}")
    cmd.run(f"git config user.email {signer_mail}")
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
