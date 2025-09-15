"""Tests for project_info module."""

from __future__ import annotations

from pathlib import Path

import pytest

from commitizen import project_info


def _create_project_files(files: dict[str, str | None]) -> None:
    for file_path, content in files.items():
        path = Path(file_path)
        if content is None:
            path.touch()
        else:
            path.write_text(content)


@pytest.mark.parametrize(
    "which_return, expected",
    [
        ("/usr/local/bin/pre-commit", True),
        (None, False),
        ("", False),
    ],
)
def test_is_pre_commit_installed(mocker, which_return, expected):
    mocker.patch("shutil.which", return_value=which_return)
    assert project_info.is_pre_commit_installed() is expected


@pytest.mark.parametrize(
    "files, expected",
    [
        (
            {"pyproject.toml": '[tool.poetry]\nname = "test"\nversion = "0.1.0"'},
            "poetry",
        ),
        ({"pyproject.toml": "", "uv.lock": ""}, "uv"),
        (
            {"pyproject.toml": '[tool.commitizen]\nversion = "0.1.0"'},
            "pep621",
        ),
        ({"setup.py": ""}, "pep621"),
        ({"Cargo.toml": ""}, "cargo"),
        ({"package.json": ""}, "npm"),
        ({"composer.json": ""}, "composer"),
        ({}, "commitizen"),
        (
            {
                "pyproject.toml": "",
                "Cargo.toml": "",
                "package.json": "",
                "composer.json": "",
            },
            "pep621",
        ),
    ],
)
def test_get_default_version_provider(chdir, files, expected):
    _create_project_files(files)
    assert project_info.get_default_version_provider() == expected


@pytest.mark.parametrize(
    "files, expected",
    [
        ({"pyproject.toml": ""}, "pyproject.toml"),
        ({}, ".cz.toml"),
    ],
)
def test_get_default_config_filename(chdir, files, expected):
    _create_project_files(files)
    assert project_info.get_default_config_filename() == expected


@pytest.mark.parametrize(
    "files, expected",
    [
        ({"pyproject.toml": ""}, "pep440"),
        ({"setup.py": ""}, "pep440"),
        ({"package.json": ""}, "semver"),
        ({}, "semver"),
    ],
)
def test_get_default_version_scheme(chdir, files, expected):
    _create_project_files(files)
    assert project_info.get_default_version_scheme() == expected
