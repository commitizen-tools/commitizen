from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from commitizen.providers import get_provider
from commitizen.providers.npm_provider import NpmProvider

if TYPE_CHECKING:
    from pathlib import Path

    from commitizen.config.base_config import BaseConfig

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

NPM_PACKAGE_JSON_LATIN1 = """\
{
  "name": "calf\u00e9-n\u00famero",
  "version": "0.1.0"
}
"""

NPM_LOCKFILE_JSON_LATIN1 = """\
{
  "name": "calf\u00e9-n\u00famero",
  "version": "0.1.0",
  "lockfileVersion": 2,
  "requires": true,
  "packages": {
    "": {
      "name": "calf\u00e9-n\u00famero",
      "version": "0.1.0"
    }
  }
}
"""


@pytest.mark.parametrize(
    ("pkg_shrinkwrap_content", "pkg_shrinkwrap_expected"),
    [(NPM_LOCKFILE_JSON, NPM_LOCKFILE_EXPECTED), (None, None)],
)
@pytest.mark.parametrize(
    ("pkg_lock_content", "pkg_lock_expected"),
    [(NPM_LOCKFILE_JSON, NPM_LOCKFILE_EXPECTED), (None, None)],
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


def test_npm_provider_respects_configured_encoding_for_all_files(
    config: BaseConfig,
    chdir: Path,
):
    """NpmProvider should use the configured encoding for all files it touches."""
    config.settings["encoding"] = "latin-1"
    config.settings["version_provider"] = "npm"

    pkg = chdir / NpmProvider.package_filename
    pkg_lock = chdir / NpmProvider.lock_filename
    pkg_shrinkwrap = chdir / NpmProvider.shrinkwrap_filename

    # Write initial contents using latin-1 encoding
    pkg.write_text(dedent(NPM_PACKAGE_JSON_LATIN1), encoding="latin-1")
    pkg_lock.write_text(dedent(NPM_LOCKFILE_JSON_LATIN1), encoding="latin-1")
    pkg_shrinkwrap.write_text(dedent(NPM_LOCKFILE_JSON_LATIN1), encoding="latin-1")

    provider = get_provider(config)
    assert isinstance(provider, NpmProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")

    # Verify that the files can be read back using the configured encoding
    pkg_text = pkg.read_text(encoding="latin-1")
    pkg_lock_text = pkg_lock.read_text(encoding="latin-1")
    pkg_shrinkwrap_text = pkg_shrinkwrap.read_text(encoding="latin-1")

    # Version was updated everywhere
    assert '"version": "42.1"' in pkg_text
    assert '"version": "42.1"' in pkg_lock_text
    assert '"version": "42.1"' in pkg_shrinkwrap_text
