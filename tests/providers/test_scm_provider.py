from __future__ import annotations


import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.scm_provider import ScmProvider
from tests.utils import (
    create_branch,
    create_file_and_commit,
    create_tag,
    merge_branch,
    switch_branch,
)


@pytest.mark.parametrize(
    "tag_format,tag,expected_version",
    (
        # If tag_format is $version (the default), version_scheme.parser is used.
        # Its DEFAULT_VERSION_PARSER allows a v prefix, but matches PEP440 otherwise.
        ("$version", "no-match-because-version-scheme-is-strict", "0.0.0"),
        ("$version", "0.1.0", "0.1.0"),
        ("$version", "v0.1.0", "0.1.0"),
        ("$version", "v-0.1.0", "0.0.0"),
        # If tag_format is not None or $version, TAG_FORMAT_REGEXS are used, which are
        # much more lenient but require a v prefix.
        ("v$version", "v0.1.0", "0.1.0"),
        ("v$version", "no-match-because-no-v-prefix", "0.0.0"),
        # no match because not a valid version
        ("v$version", "v-match-TAG_FORMAT_REGEXS", "0.0.0"),
        ("version-$version", "version-0.1.0", "0.1.0"),
        ("version-$version", "version-0.1", "0.1"),
        ("version-$version", "version-0.1.0rc1", "0.1.0rc1"),
        ("v$minor.$major.$patch", "v1.0.0", "0.1.0"),
        ("version-$major.$minor.$patch", "version-0.1.0", "0.1.0"),
        ("v$major.$minor$prerelease$devrelease", "v1.0rc1", "1.0rc1"),
        ("v$major.$minor.$patch$prerelease$devrelease", "v0.1.0", "0.1.0"),
        ("v$major.$minor.$patch$prerelease$devrelease", "v0.1.0rc1", "0.1.0rc1"),
        ("v$major.$minor.$patch$prerelease$devrelease", "v1.0.0.dev0", "1.0.0.dev0"),
    ),
)
@pytest.mark.usefixtures("tmp_git_project")
def test_scm_provider(
    config: BaseConfig, tag_format: str, tag: str, expected_version: str
):
    create_file_and_commit("test: fake commit")
    create_tag(tag)
    create_file_and_commit("test: fake commit")
    create_tag("should-not-match")

    config.settings["version_provider"] = "scm"
    config.settings["tag_format"] = tag_format

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    actual_version = provider.get_version()
    assert actual_version == expected_version

    # Should not fail on set_version()
    provider.set_version("43.1")


@pytest.mark.usefixtures("tmp_git_project")
def test_scm_provider_default_without_commits_and_tags(config: BaseConfig):
    config.settings["version_provider"] = "scm"

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    assert provider.get_version() == "0.0.0"


@pytest.mark.usefixtures("tmp_git_project")
def test_scm_provider_default_with_commits_and_tags(config: BaseConfig):
    config.settings["version_provider"] = "scm"

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    assert provider.get_version() == "0.0.0"

    create_file_and_commit("Initial state")
    create_tag("1.0.0")
    # create develop
    create_branch("develop")
    switch_branch("develop")

    # add a feature to develop
    create_file_and_commit("develop: add beta feature1")
    assert provider.get_version() == "1.0.0"
    create_tag("1.1.0b0")

    # create staging
    create_branch("staging")
    switch_branch("staging")
    create_file_and_commit("staging: Starting release candidate")
    assert provider.get_version() == "1.1.0b0"
    create_tag("1.1.0rc0")

    # add another feature to develop
    switch_branch("develop")
    create_file_and_commit("develop: add beta feature2")
    assert provider.get_version() == "1.1.0b0"
    create_tag("1.2.0b0")

    # add a hotfix to master
    switch_branch("master")
    create_file_and_commit("master: add hotfix")
    assert provider.get_version() == "1.0.0"
    create_tag("1.0.1")

    # merge the hotfix to staging
    switch_branch("staging")
    merge_branch("master")

    assert provider.get_version() == "1.1.0rc0"
