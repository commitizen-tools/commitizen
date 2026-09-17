import re
import sys
from importlib import metadata
from textwrap import dedent

import pytest

from commitizen import BaseCommitizen, defaults, factory, git
from commitizen.config import BaseConfig
from commitizen.cz import discover_plugins
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.cz.customize import CustomizeCommitsCz
from commitizen.cz.jira import JiraSmartCz
from commitizen.exceptions import NoCommitizenFoundException


class Plugin:
    pass


class OtherPlugin:
    pass


def test_factory():
    config = BaseConfig()
    config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    r = factory.committer_factory(config)
    assert isinstance(r, BaseCommitizen)


def test_default_commit_filters_keep_all_commits(config: BaseConfig):
    """Default filtering hooks preserve the original commit list."""
    cz = ConventionalCommitsCz(config)
    commits = [git.GitCommit(rev="1", title="feat: add filtering")]

    assert cz.filter_commits(commits) is commits
    assert cz.filter_commits_before_bump(commits) is commits
    assert cz.filter_commits_before_changelog(commits) is commits


def test_operation_commit_filters_delegate_to_shared_filter(config: BaseConfig, mocker):
    """Operation-specific hooks delegate to a shared custom filter."""
    cz = ConventionalCommitsCz(config)
    commits = [
        git.GitCommit(rev="1", title="feat: app a"),
        git.GitCommit(rev="2", title="feat: app b"),
    ]
    filtered_commits = commits[:1]
    filter_commits = mocker.patch.object(
        cz, "filter_commits", return_value=filtered_commits
    )

    assert cz.filter_commits_before_bump(commits) is filtered_commits
    assert cz.filter_commits_before_changelog(commits) is filtered_commits
    assert filter_commits.call_count == 2
    filter_commits.assert_any_call(commits)


def test_factory_fails():
    config = BaseConfig()
    config.settings.update({"name": "Nothing"})
    with pytest.raises(
        NoCommitizenFoundException,
        match=re.escape("The committer has not been found in the system."),
    ):
        factory.committer_factory(config)


def test_discover_plugins(tmp_path):
    legacy_plugin_folder = tmp_path / "cz_legacy"
    legacy_plugin_folder.mkdir()
    init_file = legacy_plugin_folder / "__init__.py"
    init_file.write_text(
        dedent(
            """\
    class Plugin: pass

    discover_this = Plugin
    """
        )
    )

    sys.path.append(tmp_path.as_posix())
    with pytest.warns(
        UserWarning,
        match="Legacy plugin 'cz_legacy' has been ignored: please expose it the 'commitizen.plugin' entrypoint",
    ):
        discovered_plugins = discover_plugins([tmp_path.as_posix()])
    sys.path.pop()

    assert "cz_legacy" not in discovered_plugins


def test_discover_external_plugin(mocker):
    ep_plugin = metadata.EntryPoint(
        "test", "tests.test_factory:Plugin", "commitizen.plugin"
    )
    ep_other_plugin = metadata.EntryPoint(
        "not-selected", "tests.test_factory::OtherPlugin", "commitizen.not_a_plugin"
    )
    eps = [ep_plugin, ep_other_plugin]

    def mock_entrypoints(**kwargs):
        group = kwargs.get("group")
        return metadata.EntryPoints(ep for ep in eps if ep.group == group)

    mocker.patch.object(metadata, "entry_points", side_effect=mock_entrypoints)

    assert discover_plugins() == {"test": Plugin}


def test_discover_internal_plugins():
    expected = {
        "cz_conventional_commits": ConventionalCommitsCz,
        "cz_jira": JiraSmartCz,
        "cz_customize": CustomizeCommitsCz,
    }

    discovered = discover_plugins()

    assert set(expected.items()).issubset(set(discovered.items()))
