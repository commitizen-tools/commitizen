import time
import uuid
from pathlib import Path
from typing import Optional

from commitizen import cmd, git


class FakeCommand:
    def __init__(self, out=None, err=None, return_code=0):
        self.out = out
        self.err = err
        self.return_code = return_code


def create_file_and_commit(message: str, filename: Optional[str] = None):
    if not filename:
        filename = str(uuid.uuid4())

    Path(f"./{filename}").touch()
    cmd.run("git add .")
    git.commit(message)


def wait_for_tag():
    """Wait for tag.

    The resolution of timestamps is 1 second, so we need to wait
    to create another tag unfortunately.

    This means:
    If we create 2 tags under the same second, they might be returned in the wrong order

    See https://stackoverflow.com/questions/28237043/what-is-the-resolution-of-gits-commit-date-or-author-date-timestamps
    """
    time.sleep(1.1)
