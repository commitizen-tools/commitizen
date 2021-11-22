import sys

if sys.platform == "linux":  # pragma: no cover
    import os

    # from io import IOBase

    class WrapStdinLinux:
        def __init__(self):
            fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
            tty = open(fd, "wb+", buffering=0)
            self.tty = tty

        def __getattr__(self, key):
            if key == "encoding":
                return "UTF-8"
            return getattr(self.tty, key)

        def __del__(self):
            self.tty.close()

    class WrapStdoutLinux:
        def __init__(self):
            tty = open("/dev/tty", "w")
            self.tty = tty

        def __getattr__(self, key):
            return getattr(self.tty, key)

        def __del__(self):
            self.tty.close()

    backup_stdin = None
    backup_stdout = None
    backup_stderr = None

    def _wrap_stdio():
        global backup_stdin
        backup_stdin = sys.stdin
        sys.stdin = WrapStdinLinux()

        global backup_stdout
        backup_stdout = sys.stdout
        sys.stdout = WrapStdoutLinux()

        global backup_stderr
        backup_stderr = sys.stderr
        sys.stderr = WrapStdoutLinux()

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
