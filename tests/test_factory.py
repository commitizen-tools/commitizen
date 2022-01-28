import sys

import pytest

from commitizen import BaseCommitizen, defaults, factory
from commitizen.config import BaseConfig
from commitizen.cz import discover_plugins
from commitizen.exceptions import NoCommitizenFoundException


def test_factory():
    config = BaseConfig()
    config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    r = factory.commiter_factory(config)
    assert isinstance(r, BaseCommitizen)


def test_factory_fails():
    config = BaseConfig()
    config.settings.update({"name": "Nothing"})
    with pytest.raises(NoCommitizenFoundException) as excinfo:
        factory.commiter_factory(config)

    assert "The committer has not been found in the system." in str(excinfo)


@pytest.mark.parametrize(
    "module_content, plugin_name, expected_plugins",
    [
        ("", "cz_no_plugin", {}),
    ],
)
def test_discover_plugins(module_content, plugin_name, expected_plugins, tmp_path):
    no_plugin_folder = tmp_path / plugin_name
    no_plugin_folder.mkdir()
    init_file = no_plugin_folder / "__init__.py"
    init_file.write_text(module_content)

    sys.path.append(tmp_path.as_posix())
    with pytest.warns(UserWarning) as record:
        discovered_plugins = discover_plugins([tmp_path])
    sys.path.pop()

    assert (
        record[0].message.args[0]
        == f"module '{plugin_name}' has no attribute 'discover_this'"
    )
    assert expected_plugins == discovered_plugins
