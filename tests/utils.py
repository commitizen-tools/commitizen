from __future__ import annotations

import time
import uuid
from pathlib import Path
from deprecated import deprecated

from commitizen import cmd, exceptions, git


class FakeCommand:
    def __init__(self, out=None, err=None, return_code=0):
        self.out = out
        self.err = err
        self.return_code = return_code


def create_file_and_commit(
    message: str, filename: str | None = None, committer_date: str | None = None
):
    if not filename:
        filename = str(uuid.uuid4())

    Path(filename).touch()
    c = cmd.run("git add .")
    if c.return_code != 0:
        raise exceptions.CommitError(c.err)
    c = git.commit(message, committer_date=committer_date)
    if c.return_code != 0:
        raise exceptions.CommitError(c.err)


def create_branch(name: str):
    c = cmd.run(f"git branch {name}")
    if c.return_code != 0:
        raise exceptions.GitCommandError(c.err)


def switch_branch(branch: str):
    c = cmd.run(f"git switch {branch}")
    if c.return_code != 0:
        raise exceptions.GitCommandError(c.err)


def merge_branch(branch: str):
    c = cmd.run(f"git merge {branch}")
    if c.return_code != 0:
        raise exceptions.GitCommandError(c.err)


def get_current_branch() -> str:
    c = cmd.run("git rev-parse --abbrev-ref HEAD")
    if c.return_code != 0:
        raise exceptions.GitCommandError(c.err)
    return c.out


def create_tag(tag: str, message: str | None = None) -> None:
    c = git.tag(tag, annotated=(message is not None), msg=message)
    if c.return_code != 0:
        raise exceptions.CommitError(c.err)


@deprecated(
    reason="\n\
Prefer using `create_file_and_commit(filename, committer_date={your_date})` to influence the order of tags.\n\
This is because lightweight tags (like the ones created here) use the commit's creatordate which we can specify \
with the GIT_COMMITTER_DATE flag, instead of waiting entire seconds during tests."
)
def wait_for_tag():
    """Deprecated -- use `create_file_and_commit(filename, committer_date={your_date})` to order tags instead

    Wait for tag.

    The resolution of timestamps is 1 second, so we need to wait
    to create another tag unfortunately.

    This means:
    If we create 2 tags under the same second, they might be returned in the wrong order

    See https://stackoverflow.com/questions/28237043/what-is-the-resolution-of-gits-commit-date-or-author-date-timestamps
    """
    time.sleep(1.1)
