import subprocess
from typing import NamedTuple


class Command(NamedTuple):
    out: str
    err: str
    stdout: bytes
    stderr: bytes
    rc: int


def run(cmd: str) -> Command:
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    rc = process.returncode
    return Command(stdout.decode(), stderr.decode(), stdout, stderr, rc)
