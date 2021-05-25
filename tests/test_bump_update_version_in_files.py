import re

import pytest

from commitizen import bump
from commitizen.exceptions import CurrentVersionNotFoundError

PYPROJECT = """
[tool.poetry]
name = "commitizen"
version = "1.2.3"
"""

VERSION_PY = """
__title__ = 'requests'
__description__ = 'Python HTTP for Humans.'
__url__ = 'http://python-requests.org'
__version__ = '1.2.3'
"""

INCONSISTENT_VERSION_PY = """
__title__ = 'requests'
__description__ = 'Python HTTP for Humans.'
__url__ = 'http://python-requests.org'
__version__ = '2.10.3'
"""

REPEATED_VERSION_NUMBER = """
{
  "name": "magictool",
  "version": "1.2.3",
  "dependencies": {
      "lodash": "1.2.3"
  }
}
"""

# The order cannot be guaranteed here
CARGO_LOCK = """
[[package]]
name = "textwrap"
version = "1.2.3"

[[package]]
name = "there-i-fixed-it"
version = "1.2.3"

[[package]]
name = "other-project"
version = "1.2.3"
"""

DOCKER_COMPOSE = """
version: "3.3"

services:
  app:
    image: my-repo/my-container:v1.2.3
  command: my-command
"""

MULTIPLE_VERSIONS_TO_UPDATE_POETRY_LOCK = """
[[package]]
name = "to-update-1"
version = "1.2.9"

[[package]]
name = "not-to-update"
version = "1.3.3"

[[package]]
name = "not-to-update"
version = "1.3.3"

[[package]]
name = "not-to-update"
version = "1.3.3"

[[package]]
name = "not-to-update"
version = "1.3.3"

[[package]]
name = "not-to-update"
version = "1.3.3"

[[package]]
name = "to-update-2"
version = "1.2.9"
"""

MULTIPLE_VERSIONS_INCREASE_STRING = 'version = "1.2.9"\n' * 30
MULTIPLE_VERSIONS_REDUCE_STRING = 'version = "1.2.10"\n' * 30


@pytest.fixture(scope="function")
def commitizen_config_file(tmpdir):
    tmp_file = tmpdir.join("pyproject.toml")
    tmp_file.write(PYPROJECT)
    return str(tmp_file)


@pytest.fixture(scope="function")
def python_version_file(tmpdir):
    tmp_file = tmpdir.join("__verion__.py")
    tmp_file.write(VERSION_PY)
    return str(tmp_file)


@pytest.fixture(scope="function")
def inconsistent_python_version_file(tmpdir):
    tmp_file = tmpdir.join("__verion__.py")
    tmp_file.write(INCONSISTENT_VERSION_PY)
    return str(tmp_file)


@pytest.fixture(scope="function")
def random_location_version_file(tmpdir):
    tmp_file = tmpdir.join("Cargo.lock")
    tmp_file.write(CARGO_LOCK)
    return str(tmp_file)


@pytest.fixture(scope="function")
def version_repeated_file(tmpdir):
    tmp_file = tmpdir.join("package.json")
    tmp_file.write(REPEATED_VERSION_NUMBER)
    return str(tmp_file)


@pytest.fixture(scope="function")
def multiple_versions_increase_string(tmpdir):
    tmp_file = tmpdir.join("anyfile")
    tmp_file.write(MULTIPLE_VERSIONS_INCREASE_STRING)
    return str(tmp_file)


@pytest.fixture(scope="function")
def multiple_versions_reduce_string(tmpdir):
    tmp_file = tmpdir.join("anyfile")
    tmp_file.write(MULTIPLE_VERSIONS_REDUCE_STRING)
    return str(tmp_file)


@pytest.fixture(scope="function")
def docker_compose_file(tmpdir):
    tmp_file = tmpdir.join("docker-compose.yaml")
    tmp_file.write(DOCKER_COMPOSE)
    return str(tmp_file)


@pytest.fixture(scope="function")
def multiple_versions_to_update_poetry_lock(tmpdir):
    tmp_file = tmpdir.join("pyproject.toml")
    tmp_file.write(MULTIPLE_VERSIONS_TO_UPDATE_POETRY_LOCK)
    return str(tmp_file)


@pytest.fixture(scope="function")
def version_files(
    commitizen_config_file,
    python_version_file,
    version_repeated_file,
    docker_compose_file,
):
    return [
        commitizen_config_file,
        python_version_file,
        version_repeated_file,
        docker_compose_file,
    ]


def test_update_version_in_files(version_files):
    old_version = "1.2.3"
    new_version = "2.0.0"
    bump.update_version_in_files(old_version, new_version, version_files)
    for filepath in version_files:
        with open(filepath, "r") as f:
            data = f.read()
        assert new_version in data


def test_partial_update_of_file(version_repeated_file):
    old_version = "1.2.3"
    new_version = "2.0.0"
    regex = "version"
    location = f"{version_repeated_file}:{regex}"

    bump.update_version_in_files(old_version, new_version, [location])
    with open(version_repeated_file, "r") as f:
        data = f.read()
        assert new_version in data
        assert old_version in data


def test_random_location(random_location_version_file):
    old_version = "1.2.3"
    new_version = "2.0.0"
    location = f"{random_location_version_file}:there-i-fixed-it.+\nversion"

    bump.update_version_in_files(old_version, new_version, [location])
    with open(random_location_version_file, "r") as f:
        data = f.read()
        assert len(re.findall(old_version, data)) == 2
        assert len(re.findall(new_version, data)) == 1


def test_duplicates_are_change_with_no_regex(random_location_version_file):
    old_version = "1.2.3"
    new_version = "2.0.0"
    location = f"{random_location_version_file}:version"

    bump.update_version_in_files(old_version, new_version, [location])
    with open(random_location_version_file, "r") as f:
        data = f.read()
        assert len(re.findall(old_version, data)) == 0
        assert len(re.findall(new_version, data)) == 3


def test_version_bump_increase_string_length(multiple_versions_increase_string):
    old_version = "1.2.9"
    new_version = "1.2.10"
    version_bump_change_string_size(
        multiple_versions_increase_string, old_version, new_version
    )


def test_version_bump_reduce_string_length(multiple_versions_reduce_string):
    old_version = "1.2.10"
    new_version = "2.0.0"
    version_bump_change_string_size(
        multiple_versions_reduce_string, old_version, new_version
    )


def version_bump_change_string_size(filename, old_version, new_version):
    location = f"{filename}:version"

    bump.update_version_in_files(old_version, new_version, [location])
    with open(filename, "r") as f:
        data = f.read()
        assert len(re.findall(old_version, data)) == 0
        assert len(re.findall(new_version, data)) == 30


def test_file_version_inconsistent_error(
    commitizen_config_file, inconsistent_python_version_file, version_repeated_file
):
    version_files = [
        commitizen_config_file,
        inconsistent_python_version_file,
        version_repeated_file,
    ]
    old_version = "1.2.3"
    new_version = "2.0.0"
    with pytest.raises(CurrentVersionNotFoundError) as excinfo:
        bump.update_version_in_files(
            old_version, new_version, version_files, check_consistency=True
        )

    expected_msg = (
        f"Current version 1.2.3 is not found in {inconsistent_python_version_file}.\n"
        "The version defined in commitizen configuration and the ones in "
        "version_files are possibly inconsistent."
    )
    assert expected_msg in str(excinfo.value)


def test_multiplt_versions_to_bump(multiple_versions_to_update_poetry_lock):
    old_version = "1.2.9"
    new_version = "1.2.10"
    location = f"{multiple_versions_to_update_poetry_lock}:version"

    bump.update_version_in_files(old_version, new_version, [location])
    with open(multiple_versions_to_update_poetry_lock, "r") as f:
        data = f.read()
        assert len(re.findall(old_version, data)) == 0
        assert len(re.findall(new_version, data)) == 2
