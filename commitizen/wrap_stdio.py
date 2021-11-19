import sys

if sys.platform == "win32":  # pragma: no cover
    from .wrap_stdio_windows import _unwrap_stdio, _wrap_stdio
elif sys.platform == "linux":
    from .wrap_stdio_linux import _unwrap_stdio, _wrap_stdio  # pragma: no cover
else:
    from .wrap_stdio_unix import _unwrap_stdio, _wrap_stdio  # pragma: no cover


def wrap_stdio():
    _wrap_stdio()


def unwrap_stdio():
    _unwrap_stdio()
