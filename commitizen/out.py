import io
import sys
from typing import Any

from termcolor import colored

if sys.platform == "win32":
    if isinstance(sys.stdout, io.TextIOWrapper) and sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding="utf-8")


def write(value: str, *args: object) -> None:
    """Intended to be used when value is multiline."""
    print(value, *args)


def line(value: str, *args: object, **kwargs: Any) -> None:
    """Wrapper in case I want to do something different later."""
    print(value, *args, **kwargs)


def error(value: str) -> None:
    message = colored(value, "red")
    line(message, file=sys.stderr)


def success(value: str) -> None:
    message = colored(value, "green")
    line(message)


def info(value: str) -> None:
    message = colored(value, "blue")
    line(message)


def diagnostic(value: str) -> None:
    line(value, file=sys.stderr)


def warn(value: str) -> None:
    message = colored(value, "magenta")
    line(message, file=sys.stderr)
