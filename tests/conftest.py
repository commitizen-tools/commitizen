import pytest

from commitizen import cmd


@pytest.fixture(scope="function")
def tmp_git_project(tmpdir):
    with tmpdir.as_cwd():
        cmd.run("git init")

        yield


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("tmp_git_project")
def tmp_commitizen_project(tmp_git_project):
    with open("pyproject.toml", "w") as f:
        f.write("[tool.commitizen]\n" 'version="0.1.0"')
