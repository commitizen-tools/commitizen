"""Resolves project information about the current working directory."""

import shutil
from pathlib import Path
from typing import Literal


def is_pre_commit_installed() -> bool:
    return bool(shutil.which("pre-commit"))


def get_default_version_provider() -> Literal[
    "commitizen", "cargo", "composer", "npm", "pep621", "poetry", "uv"
]:
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.is_file():
        if "[tool.poetry]" in pyproject_path.read_text():
            return "poetry"
        if Path("uv.lock").is_file():
            return "uv"
        return "pep621"

    if Path("setup.py").is_file():
        return "pep621"

    if Path("Cargo.toml").is_file():
        return "cargo"

    if Path("package.json").is_file():
        return "npm"

    if Path("composer.json").is_file():
        return "composer"

    return "commitizen"


def get_default_config_filename() -> Literal["pyproject.toml", ".cz.toml"]:
    return "pyproject.toml" if Path("pyproject.toml").is_file() else ".cz.toml"


def get_default_version_scheme() -> Literal["pep440", "semver"]:
    return (
        "pep440"
        if Path("pyproject.toml").is_file() or Path("setup.py").is_file()
        else "semver"
    )
