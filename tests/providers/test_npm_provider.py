from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.npm_provider import NpmProvider

NPM_PACKAGE_JSON = """\
{
  "name": "whatever",
  "version": "0.1.0"
}
"""

NPM_PACKAGE_EXPECTED = """\
{
  "name": "whatever",
  "version": "42.1"
}
"""

NPM_LOCKFILE_JSON = """\
{
  "name": "whatever",
  "version": "0.1.0",
  "lockfileVersion": 2,
  "requires": true,
  "packages": {
    "": {
      "name": "whatever",
      "version": "0.1.0"
    },
    "someotherpackage": {
      "version": "0.1.0"
    }
  }
}
"""

NPM_LOCKFILE_EXPECTED = """\
{
  "name": "whatever",
  "version": "42.1",
  "lockfileVersion": 2,
  "requires": true,
  "packages": {
    "": {
      "name": "whatever",
      "version": "42.1"
    },
    "someotherpackage": {
      "version": "0.1.0"
    }
  }
}
"""


@pytest.mark.parametrize(
    "pkg_shrinkwrap_content, pkg_shrinkwrap_expected",
    ((NPM_LOCKFILE_JSON, NPM_LOCKFILE_EXPECTED), (None, None)),
)
@pytest.mark.parametrize(
    "pkg_lock_content, pkg_lock_expected",
    ((NPM_LOCKFILE_JSON, NPM_LOCKFILE_EXPECTED), (None, None)),
)
def test_npm_provider(
    config: BaseConfig,
    chdir: Path,
    pkg_lock_content: str,
    pkg_lock_expected: str,
    pkg_shrinkwrap_content: str,
    pkg_shrinkwrap_expected: str,
):
    pkg = chdir / NpmProvider.package_filename
    pkg.write_text(dedent(NPM_PACKAGE_JSON))
    if pkg_lock_content:
        pkg_lock = chdir / NpmProvider.lock_filename
        pkg_lock.write_text(dedent(pkg_lock_content))
    if pkg_shrinkwrap_content:
        pkg_shrinkwrap = chdir / NpmProvider.shrinkwrap_filename
        pkg_shrinkwrap.write_text(dedent(pkg_shrinkwrap_content))
    config.settings["version_provider"] = "npm"

    provider = get_provider(config)
    assert isinstance(provider, NpmProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert pkg.read_text() == dedent(NPM_PACKAGE_EXPECTED)
    if pkg_lock_content:
        assert pkg_lock.read_text() == dedent(pkg_lock_expected)
    if pkg_shrinkwrap_content:
        assert pkg_shrinkwrap.read_text() == dedent(pkg_shrinkwrap_expected)
