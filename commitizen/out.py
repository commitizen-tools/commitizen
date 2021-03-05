import sys

from termcolor import colored


def write(value: str, *args):
    """Intended to be used when value is multiline."""
    print(value, *args)


def line(value: str, *args, **kwargs):
    """Wrapper in case I want to do something different later."""
    print(value, *args, **kwargs)


def error(value: str):
    message = colored(value, "red")
    line(message, file=sys.stderr)


def success(value: str):
    message = colored(value, "green")
    line(message)


def info(value: str):
    message = colored(value, "blue")
    line(message)


def diagnostic(value: str):
    line(value, file=sys.stderr)
