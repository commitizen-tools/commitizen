#!/usr/bin/env python

try:
    from commitizen.cz.utils import get_backup_file_path
except ImportError as error:
    print(f"could not import commitizen:\n{error}")
    exit(1)


def post_commit() -> None:
    backup_file_path = get_backup_file_path()

    # remove backup file if it exists
    if backup_file_path.is_file():
        backup_file_path.unlink()


if __name__ == "__main__":
    post_commit()
    exit(0)
