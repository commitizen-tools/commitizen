#!/usr/bin/env python
import os
import tempfile
from pathlib import Path


def post_commit():
    backup_file = Path(
        tempfile.gettempdir(), f"cz.commit{os.environ.get('USER', '')}.backup"
    )

    # remove backup file if it exists
    if backup_file.is_file():
        backup_file.unlink()


if __name__ == "__main__":
    exit(post_commit())
