from pathlib import Path
from shutil import copyfile

import pytest
from _pytest.fixtures import FixtureRequest

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
def commitizen_config_file(tmp_path: Path) -> Path:
    return _copy_sample_file_to_tmpdir(
        tmp_path, "sample_pyproject.toml", "pyproject.toml"
    )


@pytest.fixture(scope="function")
def python_version_file(tmp_path: Path, request: FixtureRequest) -> Path:
    return _copy_sample_file_to_tmpdir(tmp_path, "sample_version.py", "__version__.py")


@pytest.fixture(scope="function")
def inconsistent_python_version_file(tmp_path: Path) -> Path:
    return _copy_sample_file_to_tmpdir(
        tmp_path, "inconsistent_version.py", "__version__.py"
    )


@pytest.fixture(scope="function")
def random_location_version_file(tmp_path: Path) -> Path:
    return _copy_sample_file_to_tmpdir(tmp_path, "sample_cargo.lock", "Cargo.lock")


@pytest.fixture(scope="function")
def version_repeated_file(tmp_path: Path) -> Path:
    return _copy_sample_file_to_tmpdir(
        tmp_path, "repeated_version_number.json", "package.json"
    )


@pytest.fixture(scope="function")
def docker_compose_file(tmp_path: Path) -> Path:
    return _copy_sample_file_to_tmpdir(
        tmp_path, "sample_docker_compose.yaml", "docker-compose.yaml"
    )


@pytest.fixture(
    scope="function",
    params=(
        "multiple_versions_to_update_pyproject.toml",
        "multiple_versions_to_update_pyproject_wo_eol.toml",
    ),
    ids=("with_eol", "without_eol"),
)
def multiple_versions_to_update_poetry_lock(
    tmp_path: Path, request: FixtureRequest
) -> Path:
    return _copy_sample_file_to_tmpdir(tmp_path, request.param, "pyproject.toml")


@pytest.fixture(scope="function")
def multiple_versions_increase_string(tmp_path: Path) -> str:
    tmp_file = tmp_path / "anyfile"
    tmp_file.write_text(MULTIPLE_VERSIONS_INCREASE_STRING)
    return str(tmp_file)


@pytest.fixture(scope="function")
def multiple_versions_reduce_string(tmp_path: Path) -> str:
    tmp_file = tmp_path / "anyfile"
    tmp_file.write_text(MULTIPLE_VERSIONS_REDUCE_STRING)
    return str(tmp_file)


@pytest.fixture(scope="function")
def version_files(
    commitizen_config_file: Path,
    python_version_file: Path,
    version_repeated_file: Path,
    docker_compose_file: Path,
) -> tuple[str, ...]:
    return (
        str(commitizen_config_file),
        str(python_version_file),
        str(version_repeated_file),
        str(docker_compose_file),
    )


def test_update_version_in_files(version_files, file_regression):
    old_version = "1.2.3"
    new_version = "2.0.0"
    bump.update_version_in_files(
        old_version,
        new_version,
        version_files,
        check_consistency=False,
        encoding="utf-8",
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

    bump.update_version_in_files(
        old_version, new_version, [location], check_consistency=False, encoding="utf-8"
    )
    with open(version_repeated_file, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".json")


def test_random_location(random_location_version_file, file_regression):
    old_version = "1.2.3"
    new_version = "2.0.0"
    location = f"{random_location_version_file}:version.+Commitizen"

    bump.update_version_in_files(
        old_version, new_version, [location], check_consistency=False, encoding="utf-8"
    )
    with open(random_location_version_file, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".lock")


def test_duplicates_are_change_with_no_regex(
    random_location_version_file, file_regression
):
    old_version = "1.2.3"
    new_version = "2.0.0"
    location = f"{random_location_version_file}:version"

    bump.update_version_in_files(
        old_version, new_version, [location], check_consistency=False, encoding="utf-8"
    )
    with open(random_location_version_file, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".lock")


def test_version_bump_increase_string_length(
    multiple_versions_increase_string, file_regression
):
    old_version = "1.2.9"
    new_version = "1.2.10"
    location = f"{multiple_versions_increase_string}:version"

    bump.update_version_in_files(
        old_version, new_version, [location], check_consistency=False, encoding="utf-8"
    )
    with open(multiple_versions_increase_string, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".txt")


def test_version_bump_reduce_string_length(
    multiple_versions_reduce_string, file_regression
):
    old_version = "1.2.10"
    new_version = "2.0.0"
    location = f"{multiple_versions_reduce_string}:version"

    bump.update_version_in_files(
        old_version, new_version, [location], check_consistency=False, encoding="utf-8"
    )
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


def test_multiple_versions_to_bump(
    multiple_versions_to_update_poetry_lock, file_regression
):
    old_version = "1.2.9"
    new_version = "1.2.10"
    location = f"{multiple_versions_to_update_poetry_lock}:version"

    bump.update_version_in_files(
        old_version, new_version, [location], check_consistency=False, encoding="utf-8"
    )
    with open(multiple_versions_to_update_poetry_lock, encoding="utf-8") as f:
        file_regression.check(f.read(), extension=".toml")


def test_update_version_in_globbed_files(commitizen_config_file, file_regression):
    old_version = "1.2.3"
    new_version = "2.0.0"
    other = commitizen_config_file.parent / "other.toml"

    copyfile(commitizen_config_file, other)

    # Prepend full path as test assume absolute paths or cwd-relative
    version_files = [
        str(file_path) for file_path in commitizen_config_file.parent.glob("*.toml")
    ]

    bump.update_version_in_files(
        old_version,
        new_version,
        version_files,
        check_consistency=False,
        encoding="utf-8",
    )

    for file in commitizen_config_file, other:
        file_regression.check(file.read_text("utf-8"), extension=".toml")


def test_update_version_in_files_with_check_consistency_true(
    version_files: tuple[str, ...],
):
    """Test update_version_in_files with check_consistency=True (success case)."""
    old_version = "1.2.3"
    new_version = "2.0.0"

    # This should succeed because all files contain the current version
    updated_files: list[str] = bump.update_version_in_files(
        old_version,
        new_version,
        version_files,
        check_consistency=True,
        encoding="utf-8",
    )

    # Verify that all files were updated
    assert set(updated_files) == set(version_files)


def test_update_version_in_files_with_check_consistency_true_failure(
    commitizen_config_file, inconsistent_python_version_file
):
    """Test update_version_in_files with check_consistency=True (failure case)."""
    old_version = "1.2.3"
    new_version = "2.0.0"
    version_files = [commitizen_config_file, inconsistent_python_version_file]

    # This should fail because inconsistent_python_version_file doesn't contain the current version
    with pytest.raises(CurrentVersionNotFoundError) as excinfo:
        bump.update_version_in_files(
            old_version,
            new_version,
            version_files,
            check_consistency=True,
            encoding="utf-8",
        )

    expected_msg = (
        f"Current version {old_version} is not found in {inconsistent_python_version_file}.\n"
        "The version defined in commitizen configuration and the ones in "
        "version_files are possibly inconsistent."
    )
    assert expected_msg in str(excinfo.value)


@pytest.mark.parametrize(
    "encoding,filename",
    [
        ("latin-1", "test_latin1.txt"),
        ("utf-16", "test_utf16.txt"),
    ],
    ids=["latin-1", "utf-16"],
)
def test_update_version_in_files_with_different_encodings(tmp_path, encoding, filename):
    """Test update_version_in_files with different encodings."""
    # Create a test file with the specified encoding
    test_file = tmp_path / filename
    content = f'version = "1.2.3"\n# This is a test file with {encoding} encoding\n'
    test_file.write_text(content, encoding=encoding)

    old_version = "1.2.3"
    new_version = "2.0.0"

    updated_files = bump.update_version_in_files(
        old_version,
        new_version,
        [str(test_file)],
        check_consistency=True,
        encoding=encoding,
    )

    # Verify the file was updated
    assert len(updated_files) == 1
    assert str(test_file) in updated_files

    # Verify the content was updated correctly
    updated_content = test_file.read_text(encoding=encoding)
    assert f'version = "{new_version}"' in updated_content
    assert f'version = "{old_version}"' not in updated_content


def test_update_version_in_files_return_value(version_files):
    """Test that update_version_in_files returns the correct list of updated files."""
    old_version = "1.2.3"
    new_version = "2.0.0"

    updated_files = bump.update_version_in_files(
        old_version,
        new_version,
        version_files,
        check_consistency=False,
        encoding="utf-8",
    )

    # Verify return value is a list
    assert isinstance(updated_files, list)

    # Verify all files in the input are in the returned list
    assert set(version_files) == set(updated_files)

    # Verify the returned paths are strings
    assert all(isinstance(file_path, str) for file_path in updated_files)


def test_update_version_in_files_return_value_partial_update(tmp_path):
    """Test return value when only some files are updated."""
    # Create two test files
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    # File1 contains the version to update
    file1.write_text('version = "1.2.3"\n')

    # File2 doesn't contain the version
    file2.write_text("some other content\n")

    old_version = "1.2.3"
    new_version = "2.0.0"

    updated_files = bump.update_version_in_files(
        old_version,
        new_version,
        [str(file1), str(file2)],
        check_consistency=False,
        encoding="utf-8",
    )

    # Verify return value
    assert isinstance(updated_files, list)
    assert len(updated_files) == 2  # Both files should be in the list
    assert str(file1) in updated_files
    assert str(file2) in updated_files

    # Verify file1 was actually updated
    content1 = file1.read_text(encoding="utf-8")
    assert f'version = "{new_version}"' in content1

    # Verify file2 was not changed
    content2 = file2.read_text(encoding="utf-8")
    assert content2 == "some other content\n"
