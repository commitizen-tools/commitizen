from __future__ import annotations

import json

import pytest
import tomlkit
import yaml

from commitizen.commands.dump_config import DumpConfig
from commitizen.config import BaseConfig


@pytest.fixture
def config() -> BaseConfig:
    cfg = BaseConfig()
    return cfg


def test_dump_config_toml(config, capsys):
    DumpConfig(config, {"format": "toml"})()
    out, _ = capsys.readouterr()
    doc = tomlkit.loads(out)
    assert "tool" in doc
    assert "commitizen" in doc["tool"]
    cz = doc["tool"]["commitizen"]
    assert cz["name"] == "cz_conventional_commits"


def test_dump_config_yaml(config, capsys):
    DumpConfig(config, {"format": "yaml"})()
    out, _ = capsys.readouterr()
    data = yaml.safe_load(out)
    assert "tool" in data
    assert "commitizen" in data["tool"]
    assert data["tool"]["commitizen"]["name"] == "cz_conventional_commits"


def test_dump_config_json(config, capsys):
    DumpConfig(config, {"format": "json"})()
    out, _ = capsys.readouterr()
    data = json.loads(out)
    assert "tool" in data
    assert "commitizen" in data["tool"]
    assert data["tool"]["commitizen"]["name"] == "cz_conventional_commits"


def test_dump_config_toml_default_format(config, capsys):
    """Test that toml is the default format."""
    DumpConfig(config, {})()
    out, _ = capsys.readouterr()
    doc = tomlkit.loads(out)
    assert "tool" in doc


def test_dump_config_toml_no_none_values(config, capsys):
    """Test that None values are filtered out in TOML output."""
    DumpConfig(config, {"format": "toml"})()
    out, _ = capsys.readouterr()
    assert "null" not in out.lower()
    doc = tomlkit.loads(out)
    cz = doc["tool"]["commitizen"]
    for value in cz.values():
        assert value is not None
