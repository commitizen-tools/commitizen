import subprocess
from typing import NamedTuple

from charset_normalizer import from_bytes


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
        str(from_bytes(stdout).best()),
        str(from_bytes(stderr).best()),
        stdout,
        stderr,
        return_code,
    )
