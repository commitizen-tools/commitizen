from termcolor import colored


def write(value: str, *args):
    """Intended to be used when value is multiline."""
    print(value, *args)


def line(value: str, *args):
    """Wrapper in case I want to do something different later."""
    print(value, *args)


def error(value: str):
    """TODO: This should go to stderr."""
    message = colored(value, "red")
    line(message)


def success(value: str):
    message = colored(value, "green")
    line(message)


def info(value: str):
    message = colored(value, "blue")
    line(message)
