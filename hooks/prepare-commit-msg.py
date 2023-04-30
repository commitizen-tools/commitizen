#!/usr/bin/env python
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from subprocess import CalledProcessError


def prepare_commit_msg(commit_msg_file: Path) -> int:
    # check that commitizen is installed
    if shutil.which("cz") is None:
        print("commitizen is not installed!")
        return 0

    # check if the commit message needs to be generated using commitizen
    if (
        subprocess.run(
            [
                "cz",
                "check",
                "--commit-msg-file",
                commit_msg_file,
            ],
            capture_output=True,
        ).returncode
        != 0
    ):
        backup_file = Path(
            tempfile.gettempdir(), f"cz.commit{os.environ.get('USER', '')}.backup"
        )

        if backup_file.is_file():
            # confirm if commit message from backup file should be reused
            answer = input("retry with previous message? [y/N]: ")
            if answer.lower() == "y":
                shutil.copyfile(backup_file, commit_msg_file)
                return 0

        # use commitizen to generate the commit message
        try:
            subprocess.run(
                [
                    "cz",
                    "commit",
                    "--dry-run",
                    "--write-message-to-file",
                    commit_msg_file,
                ],
                stdin=sys.stdin,
                stdout=sys.stdout,
            ).check_returncode()
        except CalledProcessError as error:
            return error.returncode

        # write message to backup file
        shutil.copyfile(commit_msg_file, backup_file)


if __name__ == "__main__":
    # make hook interactive by attaching /dev/tty to stdin
    with open("/dev/tty") as tty:
        sys.stdin = tty
        exit(prepare_commit_msg(sys.argv[1]))
