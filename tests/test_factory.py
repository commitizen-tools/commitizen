import sys
from textwrap import dedent

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

import pytest

from commitizen import BaseCommitizen, defaults, factory
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


def test_factory_fails():
    config = BaseConfig()
    config.settings.update({"name": "Nothing"})
    with pytest.raises(NoCommitizenFoundException) as excinfo:
        factory.committer_factory(config)

    assert "The committer has not been found in the system." in str(excinfo)


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
    with pytest.warns(UserWarning) as record:
        discovered_plugins = discover_plugins([tmp_path.as_posix()])
    sys.path.pop()

    assert (
        record[0].message.args[0]
        == "Legacy plugin 'cz_legacy' has been ignored: please expose it the 'commitizen.plugin' entrypoint"
    )
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
