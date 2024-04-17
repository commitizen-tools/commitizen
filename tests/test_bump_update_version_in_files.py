from pathlib import Path
from shutil import copyfile

import pytest

from commitizen import bump
from commitizen.exceptions import CurrentVersionNotFoundError

MULTIPLE_VERSIONS_INCREASE_STRING = 'version = "1.2.9"\n' * 30
MULTIPLE_VERSIONS_REDUCE_STRING = 'version = "1.2.10"\n' * 30

TESTING_FILE_PREFIX = "tests/data"


def _copy_sample_file_to_tmpdir(
    tmp_path: Path, source_filename: str, dest_filename: str
) -> Path:
    tmp_file = tmp_path / dest_filename
    copyfile(f"{TESTING_FILE_PREFIX}/{source_filename}", tmp_file)
    return tmp_file


@pytest.fixture(scope="function")
def commitizen_config_file(tmpdir):
    return _copy_sample_file_to_tmpdir(
        tmpdir, "sample_pyproject.toml", "pyproject.toml"
    )


@pytest.fixture(scope="function")
def python_version_file(tmpdir, request):
    return _copy_sample_file_to_tmpdir(tmpdir, "sample_version.py", "__version__.py")


@pytest.fixture(scope="function")
def inconsistent_python_version_file(tmpdir):
    return _copy_sample_file_to_tmpdir(
        tmpdir, "inconsistent_version.py", "__version__.py"
    )


@pytest.fixture(scope="function")
def random_location_version_file(tmpdir):
    return _copy_sample_file_to_tmpdir(tmpdir, "sample_cargo.lock", "Cargo.lock")


@pytest.fixture(scope="function")
def version_repeated_file(tmpdir):
    return _copy_sample_file_to_tmpdir(
        tmpdir, "repeated_version_number.json", "package.json"
    )


@pytest.fixture(scope="function")
def docker_compose_file(tmpdir):
    return _copy_sample_file_to_tmpdir(
        tmpdir, "sample_docker_compose.yaml", "docker-compose.yaml"
    )


@pytest.fixture(
    scope="function",
    params=(
        "multiple_versions_to_update_pyproject.toml",
        "multiple_versions_to_update_pyproject_wo_eol.toml",
    ),
    ids=("with_eol", "without_eol"),
)
def multiple_versions_to_update_poetry_lock(tmpdir, request):
    return _copy_sample_file_to_tmpdir(tmpdir, request.param, "pyproject.toml")


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
def version_files(
    commitizen_config_file,
    python_version_file,
    version_repeated_file,
    docker_compose_file,
):
    return (
        commitizen_config_file,
        python_version_file,
        version_repeated_file,
        docker_compose_file,
    )


def test_update_version_in_files(version_files, file_regression):
    old_version = "1.2.3"
    new_version = "2.0.0"
    bump.update_version_in_files(
        old_version, new_version, version_files, encoding="utf-8"
    )

    file_contents = ""
    for filepath in version_files:
        with open(filepath, encoding="utf-8") as f:
            file_contents += f.read()
    file_regression.check(file_contents, extension=".txt")


def test_partial_update_of_file(version_repeated_file, file_regression):
    old_version = "1.2.3"
    new_version = "2.0.0"
    regex = "version"
    location = f"{version_repeated_file}:{regex}"

    bump.update_version_in_files(old_version, new_version, [location], encoding="utf-8")
    with open(version_repeated_file, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".json")


def test_random_location(random_location_version_file, file_regression):
    old_version = "1.2.3"
    new_version = "2.0.0"
    location = f"{random_location_version_file}:version.+Commitizen"

    bump.update_version_in_files(old_version, new_version, [location], encoding="utf-8")
    with open(random_location_version_file, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".lock")


def test_duplicates_are_change_with_no_regex(
    random_location_version_file, file_regression
):
    old_version = "1.2.3"
    new_version = "2.0.0"
    location = f"{random_location_version_file}:version"

    bump.update_version_in_files(old_version, new_version, [location], encoding="utf-8")
    with open(random_location_version_file, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".lock")


def test_version_bump_increase_string_length(
    multiple_versions_increase_string, file_regression
):
    old_version = "1.2.9"
    new_version = "1.2.10"
    location = f"{multiple_versions_increase_string}:version"

    bump.update_version_in_files(old_version, new_version, [location], encoding="utf-8")
    with open(multiple_versions_increase_string, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".txt")


def test_version_bump_reduce_string_length(
    multiple_versions_reduce_string, file_regression
):
    old_version = "1.2.10"
    new_version = "2.0.0"
    location = f"{multiple_versions_reduce_string}:version"

    bump.update_version_in_files(old_version, new_version, [location], encoding="utf-8")
    with open(multiple_versions_reduce_string, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".txt")


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
            old_version,
            new_version,
            version_files,
            check_consistency=True,
            encoding="utf-8",
        )

    expected_msg = (
        f"Current version 1.2.3 is not found in {inconsistent_python_version_file}.\n"
        "The version defined in commitizen configuration and the ones in "
        "version_files are possibly inconsistent."
    )
    assert expected_msg in str(excinfo.value)


def test_multiplt_versions_to_bump(
    multiple_versions_to_update_poetry_lock, file_regression
):
    old_version = "1.2.9"
    new_version = "1.2.10"
    location = f"{multiple_versions_to_update_poetry_lock}:version"

    bump.update_version_in_files(old_version, new_version, [location], encoding="utf-8")
    with open(multiple_versions_to_update_poetry_lock, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".toml")


def test_update_version_in_globbed_files(commitizen_config_file, file_regression):
    old_version = "1.2.3"
    new_version = "2.0.0"
    other = commitizen_config_file.dirpath("other.toml")
    print(commitizen_config_file, other)
    copyfile(commitizen_config_file, other)

    # Prepend full ppath as test assume absolute paths or cwd-relative
    version_files = [commitizen_config_file.dirpath("*.toml")]

    bump.update_version_in_files(
        old_version, new_version, version_files, encoding="utf-8"
    )

    for file in commitizen_config_file, other:
        file_regression.check(file.read_text("utf-8"), extension=".toml")
