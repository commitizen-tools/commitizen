import os
import selectors
import sys
from asyncio import DefaultEventLoopPolicy, get_event_loop_policy, set_event_loop_policy
from io import IOBase


class CZEventLoopPolicy(DefaultEventLoopPolicy):  # type: ignore
    def get_event_loop(self):
        self.set_event_loop(self._loop_factory(selectors.SelectSelector()))
        return self._local._loop


class WrapStdioUnix:
    def __init__(self, stdx: IOBase):
        self._fileno = stdx.fileno()
        fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
        if self._fileno == 0:
            tty = open(fd, "wb+", buffering=0)
        else:
            tty = open(fd, "rb+", buffering=0)
        self.tty = tty

    def __getattr__(self, key):
        if key == "encoding":
            return "UTF-8"
        return getattr(self.tty, key)

    def __del__(self):
        self.tty.close()


backup_event_loop_policy = None
backup_stdin = None
backup_stdout = None
backup_stderr = None


def _wrap_stdio():
    global backup_event_loop_policy
    backup_event_loop_policy = get_event_loop_policy()
    set_event_loop_policy(CZEventLoopPolicy())

    global backup_stdin
    backup_stdin = sys.stdin
    sys.stdin = WrapStdioUnix(sys.stdin)

    global backup_stdout
    backup_stdout = sys.stdout
    sys.stdout = WrapStdioUnix(sys.stdout)

    global backup_stderr
    backup_stdout = sys.stderr
    sys.stderr = WrapStdioUnix(sys.stderr)


def _unwrap_stdio():
    global backup_event_loop_policy
    set_event_loop_policy(backup_event_loop_policy)

    global backup_stdin
    sys.stdin.close()
    sys.stdin = backup_stdin

    global backup_stdout
    sys.stdout.close()
    sys.stdout = backup_stdout

    global backup_stderr
    sys.stderr.close()
    sys.stderr = backup_stderr
