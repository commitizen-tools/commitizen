import os
import shutil
import stat, errno
import sys
import uuid
from pathlib import Path
from typing import Optional

import pytest

from commitizen import cli, cmd, git

# https://stackoverflow.com/questions/1213706/what-user-do-python-scripts-run-as-in-windows
def handleRemoveReadOnly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, shutil.rmtree) and excvalue.errno == errno.EACCESS:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.IRWXO) #744
        func(path)
    else:
        raise

@pytest.fixture
def create_project():
    current_directory = os.getcwd()
    tmp_proj_path = "tests/tmp-proj"
    full_tmp_path = os.path.join(current_directory, tmp_proj_path)
    if not os.path.exists(full_tmp_path):
        os.makedirs(full_tmp_path)
    os.chdir(full_tmp_path)
    yield
    os.chdir(current_directory)
    shutil.rmtree(full_tmp_path, handleRemoveReadOnly)


def create_file_and_commit(message: str, filename: Optional[str] = None):
    if not filename:
        filename = str(uuid.uuid4())
    Path(f"./{filename}").touch()
    cmd.run("git add .")
    git.commit(message)


def test_bump_command(mocker, create_project):
    with open("./pyproject.toml", "w") as f:
        f.write("[tool.commitizen]\n" 'version="0.1.0"')

    cmd.run("git init")

    # MINOR
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    # PATCH
    create_file_and_commit("fix: username exception")

    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.1")
    assert tag_exists is True

    # PRERELEASE
    create_file_and_commit("feat: location")

    testargs = ["cz", "bump", "--prerelease", "alpha"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.3.0a0")
    assert tag_exists is True

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.3.0")
    assert tag_exists is True

    # MAJOR
    create_file_and_commit(
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported"
    )

    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("1.0.0")
    assert tag_exists is True
