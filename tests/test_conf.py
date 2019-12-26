import os

import pytest

from commitizen import config, defaults

PYPROJECT = """
[tool.commitizen]
name = "cz_jira"
version = "1.0.0"
version_files = [
    "commitizen/__version__.py",
    "pyproject.toml"
]
style = [
    ["pointer", "reverse"],
    ["question", "underline"]
]

[tool.black]
line-length = 88
target-version = ['py36', 'py37', 'py38']
"""

RAW_CONFIG = """
[commitizen]
name = cz_jira
version = 1.0.0
version_files = [
    "commitizen/__version__.py",
    "pyproject.toml"
    ]
style = [
    ["pointer", "reverse"],
    ["question", "underline"]
    ]
"""

_settings = {
    "name": "cz_jira",
    "version": "1.0.0",
    "tag_format": None,
    "bump_message": None,
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
}

_new_settings = {
    "name": "cz_jira",
    "version": "2.0.0",
    "tag_format": None,
    "bump_message": None,
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
}

_read_settings = {
    "name": "cz_jira",
    "version": "1.0.0",
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
}


@pytest.fixture
def configure_supported_files():
    original = defaults.config_files.copy()

    # patch the defaults to include tests
    defaults.config_files = [os.path.join("tests", f) for f in defaults.config_files]
    yield
    defaults.config_files = original


@pytest.fixture
def config_files_manager(request):
    filename = request.param
    filepath = os.path.join("tests", filename)
    with open(filepath, "w") as f:
        if "toml" in filename:
            f.write(PYPROJECT)
        else:
            f.write(RAW_CONFIG)
    yield
    os.remove(filepath)


@pytest.fixture
def empty_pyproject_ok_cz():
    pyproject = "tests/pyproject.toml"
    cz = "tests/.cz"
    with open(pyproject, "w") as f:
        f.write("")
    with open(cz, "w") as f:
        f.write(RAW_CONFIG)
    yield
    os.remove(pyproject)
    os.remove(cz)


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_load_conf(config_files_manager, configure_supported_files):
    cfg = config.read_cfg()
    assert cfg.settings == _settings


def test_conf_is_loaded_with_empty_pyproject_but_ok_cz(
    empty_pyproject_ok_cz, configure_supported_files
):
    cfg = config.read_cfg()
    assert cfg.settings == _settings


def test_conf_returns_default_when_no_files(configure_supported_files):
    cfg = config.read_cfg()
    assert cfg.settings == defaults.DEFAULT_SETTINGS


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_set_key(configure_supported_files, config_files_manager):
    _conf = config.read_cfg()
    _conf.set_key("version", "2.0.0")
    cfg = config.read_cfg()
    assert cfg.settings == _new_settings
