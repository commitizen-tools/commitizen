import subprocess
from typing import NamedTuple


class Command(NamedTuple):
    out: str
    err: str
    stdout: bytes
    stderr: bytes


def run(cmd: str) -> Command:
    cmd.split()
    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return Command(stdout.decode(), stderr.decode(), stdout, stderr)
