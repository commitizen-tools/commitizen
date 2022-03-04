import sys

from termcolor import colored


def write(value: str, *args) -> None:
    """Intended to be used when value is multiline."""
    print(value, *args)


def line(value: str, *args, **kwargs) -> None:
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


def diagnostic(value: str):
    line(value, file=sys.stderr)


def warn(value: str) -> None:
    message = colored(value, "magenta")
    line(message)
