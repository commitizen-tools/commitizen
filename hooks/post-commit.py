#!/usr/bin/env python
from pathlib import Path

try:
    from commitizen.cz.utils import get_backup_file_path
except ImportError as error:
    print(f"could not import commitizen:\n{error}")
    exit(1)


def post_commit():
    backup_file = Path(get_backup_file_path())

    # remove backup file if it exists
    if backup_file.is_file():
        backup_file.unlink()


if __name__ == "__main__":
    exit(post_commit())
