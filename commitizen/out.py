import io
import sys
from typing import Any

from termcolor import colored


def _ensure_utf8_stdout(stream: object) -> None:
    """Reconfigure non-UTF-8 stdout streams to emit UTF-8 bytes.

    The primary fix is switching stdout from locale-dependent encodings to
    UTF-8 so normal Unicode output (for example, ``\U0001f680`` 🚀 or the
    ``\u2019`` typographic apostrophe) does not raise ``UnicodeEncodeError`` on:

    * Windows ``cmd.exe`` defaulting to ``cp1252`` (the historical case),
    * Linux/macOS terminals with a non-UTF-8 ``LANG`` such as
      ``de_CH.ISO8859-1`` (#956).

    ``errors="replace"`` is a defensive fallback for genuinely
    un-encodable input, such as lone surrogates produced by buggy callers.
    It does not make terminals render bytes; rendering is handled after the
    encoder has produced UTF-8 bytes.
    """
    if not isinstance(stream, io.TextIOWrapper):
        return
    encoding = (stream.encoding or "").lower().replace("-", "").replace("_", "")
    if encoding == "utf8":
        return
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - safety net
        pass


_ensure_utf8_stdout(sys.stdout)


def write(value: object, *args: object) -> None:
    """Intended to be used when value is multiline."""
    print(value, *args)


def line(value: object, *args: object, **kwargs: Any) -> None:
    """Wrapper in case I want to do something different later."""
    print(value, *args, **kwargs)


def error(value: object) -> None:
    message = colored(str(value), "red")
    line(message, file=sys.stderr)


def success(value: object) -> None:
    message = colored(str(value), "green")
    line(message)


def info(value: object) -> None:
    message = colored(str(value), "blue")
    line(message)


def diagnostic(value: object) -> None:
    line(value, file=sys.stderr)


def warn(value: object) -> None:
    message = colored(str(value), "magenta")
    line(message, file=sys.stderr)
