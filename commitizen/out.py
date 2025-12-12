import io
import sys
from typing import Any

from termcolor import colored

if sys.platform == "win32":
    if isinstance(sys.stdout, io.TextIOWrapper) and sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding="utf-8")


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
