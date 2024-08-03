from __future__ import annotations

import pytest

import os

from commitizen.config.base_config import BaseConfig
from commitizen.providers.mvn_provider import MavenProvider


def test_can_run_subcommand(config: BaseConfig):
    provider = MavenProvider(config)
    got = provider._MavenProvider__run_cmd("echo 'hi'")  # type: ignore
    expected = "hi"
    assert got == expected


@pytest.mark.parametrize(
    "file, expected",
    (
        ("./tests/data/sample_pom.xml", "3.2.1"),
        ("./tests/data/sample_pom_snapshot.xml", "3.2.1-SNAPSHOT"),
    ),
)
def test_get_version(config: BaseConfig, file: str, expected: str):
    provider = MavenProvider(config)
    got = provider.get_version(file)
    assert got == expected


def test_set_version(config: BaseConfig):
    provider = MavenProvider(config)
    file = "./tests/data/sample_pom.xml"
    expected = "3.2.2"
    provider.set_version(expected, file)
    got = provider.get_version(file)
    assert got == expected

    # rollback changes
    expected = "3.2.1"
    provider.set_version(expected, file)
    got = provider.get_version(file)
    assert got == expected

    # delete backup file created
    backup_file = file + ".versionsBackup"
    assert os.path.exists(backup_file)
    if os.path.exists(backup_file):
        os.remove(backup_file)
    assert not os.path.exists(backup_file)
