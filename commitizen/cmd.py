import subprocess
from typing import NamedTuple

import chardet


class Command(NamedTuple):
    out: str
    err: str
    stdout: bytes
    stderr: bytes
    return_code: int


def run(cmd: str) -> Command:
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    return_code = process.returncode
    return Command(
        stdout.decode(chardet.detect(stdout)["encoding"] or "utf-8"),
        stderr.decode(chardet.detect(stderr)["encoding"] or "utf-8"),
        stdout,
        stderr,
        return_code,
    )
