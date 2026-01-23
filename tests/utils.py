from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import pytest

from commitizen import cli, cmd, exceptions, git
from commitizen.cmd import Command

if TYPE_CHECKING:
    from unittest.mock import Mock

    from freezegun.api import FrozenDateTimeFactory
    from pytest_mock import MockerFixture

    from commitizen.version_schemes import Increment, Prerelease


class VersionSchemeTestArgs(NamedTuple):
    current_version: str
    increment: Increment | None
    prerelease: Prerelease | None
    prerelease_offset: int
    devrelease: int | None
    postrelease: bool


@dataclass
class UtilFixture:
    """
    An helper fixture providing most common operations for tests.

    git and cli operations grant control over time.
    """

    mocker: MockerFixture
    monkeypatch: pytest.MonkeyPatch
    freezer: FrozenDateTimeFactory

    def __post_init__(self):
        self.patch_env()

    def create_file_and_commit(
        self,
        message: str,
        filename: str | None = None,
        committer_date: str | None = None,
    ) -> None:
        """Create a file and commit it."""
        if not filename:
            filename = str(uuid.uuid4())

        Path(filename).touch()
        c = cmd.run("git add .")
        if c.return_code != 0:
            raise exceptions.CommitError(c.err)
        c = git.commit(message, committer_date=committer_date)
        if c.return_code != 0:
            raise exceptions.CommitError(c.err)
        self.tick()

    def create_branch(self, name: str) -> None:
        """Create a new branch."""
        c = cmd.run(f"git branch {name}")
        if c.return_code != 0:
            raise exceptions.GitCommandError(c.err)

    def switch_branch(self, branch: str) -> None:
        """Switch to given branch."""
        c = cmd.run(f"git switch {branch}")
        if c.return_code != 0:
            raise exceptions.GitCommandError(c.err)

    def merge_branch(self, branch: str) -> None:
        """Merge given branch into current branch."""
        c = cmd.run(f"git merge {branch}")
        if c.return_code != 0:
            raise exceptions.GitCommandError(c.err)
        self.tick()

    def get_current_branch(self) -> str:
        """Get current git branch name."""
        c = cmd.run("git rev-parse --abbrev-ref HEAD")
        if c.return_code != 0:
            raise exceptions.GitCommandError(c.err)
        return c.out

    def create_tag(
        self, tag: str, message: str | None = None, annotated: bool | None = None
    ) -> None:
        """Create a git tag."""
        c = git.tag(
            tag, annotated=(annotated is True or message is not None), msg=message
        )
        if c.return_code != 0:
            raise exceptions.CommitError(c.err)
        self.tick()

    def run_cli(self, *args: str) -> None:
        """Execute commitizen CLI with given args."""
        self.mocker.patch.object(sys, "argv", ["cz", *args])
        cli.main()
        self.tick()

    def patch_env(self) -> None:
        """Patch environment variables to sync with FreezeGun time."""
        self.monkeypatch.setenv("DATE", datetime.now().isoformat())
        self.monkeypatch.setenv("GIT_AUTHOR_DATE", datetime.now().isoformat())
        self.monkeypatch.setenv("GIT_COMMITTER_DATE", datetime.now().isoformat())

    def tick(self) -> None:
        """Advance time by 1 second."""
        self.freezer.tick()
        self.patch_env()

    def mock_cmd(self, out: str = "", err: str = "", return_code: int = 0) -> Mock:
        """Mock cmd.run command."""
        return_value = Command(out, err, b"", b"", return_code)
        return self.mocker.patch("commitizen.cmd.run", return_value=return_value)


@pytest.fixture
def util(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    freezer: FrozenDateTimeFactory,
) -> UtilFixture:
    """An helper fixture"""
    return UtilFixture(mocker=mocker, monkeypatch=monkeypatch, freezer=freezer)
