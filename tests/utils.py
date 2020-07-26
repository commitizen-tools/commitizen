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
