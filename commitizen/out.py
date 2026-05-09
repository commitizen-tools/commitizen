import io
import sys
from typing import Any

from termcolor import colored


def _ensure_utf8_stdout(stream: object) -> None:
    """Reconfigure ``stream`` to UTF-8 if its current encoding can't represent
    the unicode characters commitizen emits (e.g. ``\U0001f680`` 🚀, the
    ``\u2019`` typographic apostrophe).

    Without this, ``print`` raises ``UnicodeEncodeError`` mid-output on:

    * Windows ``cmd.exe`` defaulting to ``cp1252`` (the historical case),
    * Linux/macOS terminals with a non-UTF-8 ``LANG`` such as
      ``de_CH.ISO8859-1`` (#956).

    ``errors="replace"`` is used as a safety net for terminals that
    genuinely can't render the bytes, so commitizen falls back to a
    placeholder character instead of crashing.
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
