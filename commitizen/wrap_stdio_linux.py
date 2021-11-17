import os
import sys
from io import IOBase


class WrapStdioLinux:
    def __init__(self, stdx: IOBase):
        self._fileno = stdx.fileno()
        if self._fileno == 0:
            fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
            tty = open(fd, "wb+", buffering=0)
        else:
            tty = open("/dev/tty", "w")  # type: ignore
        self.tty = tty

    def __getattr__(self, key):
        if key == "encoding" and self._fileno == 0:
            return "UTF-8"
        return getattr(self.tty, key)

    def __del__(self):
        self.tty.close()


backup_stdin = None
backup_stdout = None
backup_stderr = None


def _wrap_stdio():
    global backup_stdin
    backup_stdin = sys.stdin
    sys.stdin = WrapStdioLinux(sys.stdin)

    global backup_stdout
    backup_stdout = sys.stdout
    sys.stdout = WrapStdioLinux(sys.stdout)

    global backup_stderr
    backup_stderr = sys.stderr
    sys.stderr = WrapStdioLinux(sys.stderr)


def _unwrap_stdio():
    global backup_stdin
    sys.stdin.close()
    sys.stdin = backup_stdin

    global backup_stdout
    sys.stdout.close()
    sys.stdout = backup_stdout

    global backup_stderr
    sys.stderr.close()
    sys.stderr = backup_stderr
