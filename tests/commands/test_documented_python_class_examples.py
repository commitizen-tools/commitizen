"""Tests for executable custom-plugin examples published in the docs."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from commitizen import git
from commitizen.cz import registry
from commitizen.exceptions import NoneIncrementExit

if TYPE_CHECKING:
    from pytest_mock import MockFixture

    from commitizen.cz.base import BaseCommitizen
    from tests.utils import UtilFixture


DOCUMENTED_PLUGIN_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "examples" / "cz_docs_only.py"
)


def _load_documented_plugin() -> type[BaseCommitizen]:
    """Load the custom plugin example from the file embedded in the docs."""
    spec = importlib.util.spec_from_file_location(
        "tests_documented_cz_docs_only", DOCUMENTED_PLUGIN_PATH
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return cast("type[BaseCommitizen]", getattr(module, "DocsOnlyPatchCommitizen"))


@pytest.fixture
def documented_plugin_name(mocker: MockFixture) -> str:
    """Expose the documented example through Commitizen's plugin registry."""
    plugin_name = "cz_docs_only"
    plugin_class = _load_documented_plugin()
    mocker.patch.dict("commitizen.cz.registry", {**registry, plugin_name: plugin_class})
    return plugin_name


@pytest.mark.parametrize("major_version_zero", [False, True])
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_documented_python_plugin_fix_commit_bumps_patch(
    util: UtilFixture, documented_plugin_name: str, major_version_zero: bool
) -> None:
    """The documented example bumps a fix commit as a patch release."""
    util.create_file_and_commit("fix: ship executable docs example")

    args = ["--name", documented_plugin_name, "bump", "--yes"]
    if major_version_zero:
        args.append("--major-version-zero")
    util.run_cli(*args)

    assert git.tag_exist("0.1.1") is True


@pytest.mark.parametrize("major_version_zero", [False, True])
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_documented_python_plugin_docs_commit_does_not_bump(
    util: UtilFixture, documented_plugin_name: str, major_version_zero: bool
) -> None:
    """The documented example treats docs commits as a no-bump match."""
    first_bump_args = ["--name", documented_plugin_name, "bump", "--yes"]
    if major_version_zero:
        first_bump_args.append("--major-version-zero")

    util.create_file_and_commit("fix: seed release")
    util.run_cli(*first_bump_args)
    util.create_file_and_commit("docs: expand plugin guide")

    with pytest.raises(NoneIncrementExit):
        util.run_cli(*first_bump_args)

    assert git.tag_exist("0.1.2") is False
