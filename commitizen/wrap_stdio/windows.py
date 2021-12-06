import sys

if sys.platform == "win32":  # pragma: no cover
    import msvcrt
    import os
    from ctypes import c_ulong, windll  # noqa
    from ctypes.wintypes import HANDLE
    from io import IOBase

    STD_INPUT_HANDLE = c_ulong(-10)
    STD_OUTPUT_HANDLE = c_ulong(-11)

    class WrapStdioWindows:
        def __init__(self, stdx: IOBase):
            self._fileno = stdx.fileno()
            if self._fileno == 0:
                fd = os.open("CONIN$", os.O_RDWR | os.O_BINARY)
                tty = open(fd)
                handle = HANDLE(msvcrt.get_osfhandle(fd))  # noqa
                windll.kernel32.SetStdHandle(STD_INPUT_HANDLE, handle)
            elif self._fileno == 1:
                fd = os.open("CONOUT$", os.O_RDWR | os.O_BINARY)
                tty = open(fd, "w")
                handle = HANDLE(msvcrt.get_osfhandle(fd))  # noqa
                windll.kernel32.SetStdHandle(STD_OUTPUT_HANDLE, handle)
            else:
                raise Exception("not defined type")
            self._tty = tty

        def __getattr__(self, key):
            if key == "encoding" and self._fileno == 0:
                return "UTF-8"
            return getattr(self._tty, key)

        def __del__(self):
            if "_tty" in self.__dict__:
                self._tty.close()

    backup_stdin = None
    backup_stdout = None

    def _wrap_stdio():
        global backup_stdin
        backup_stdin = sys.stdin
        sys.stdin = WrapStdioWindows(sys.stdin)

        global backup_stdout
        backup_stdout = sys.stdout
        sys.stdout = WrapStdioWindows(sys.stdout)

    def _unwrap_stdio():
        global backup_stdin
        sys.stdin.close()
        sys.stdin = backup_stdin

        global backup_stdout
        sys.stdout.close()
        sys.stdout = backup_stdout
