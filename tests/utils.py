import uuid
from pathlib import Path
from typing import Optional

from commitizen import cmd, git


def create_file_and_commit(message: str, filename: Optional[str] = None):
    if not filename:
        filename = str(uuid.uuid4())

    Path(f"./{filename}").touch()
    cmd.run("git add .")
    git.commit(message)
