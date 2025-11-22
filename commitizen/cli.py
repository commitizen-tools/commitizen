from __future__ import annotations

import argparse
import logging
import sys
from functools import partial
from types import TracebackType
from typing import TYPE_CHECKING, cast

import argcomplete

from commitizen import commands, config, out
from commitizen.decli_parser import get_parser
from commitizen.exceptions import (
    CommitizenException,
    ExitCode,
    ExpectedExit,
    InvalidCommandArgumentError,
    NoCommandFoundError,
)

logger = logging.getLogger(__name__)


original_excepthook = sys.excepthook


def commitizen_excepthook(
    type: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
    debug: bool = False,
    no_raise: list[int] | None = None,
) -> None:
    traceback = traceback if isinstance(traceback, TracebackType) else None
    if not isinstance(value, CommitizenException):
        original_excepthook(type, value, traceback)
        return

    if not no_raise:
        no_raise = []
    if value.message:
        value.output_method(value.message)
    if debug:
        original_excepthook(type, value, traceback)
    exit_code = value.exit_code
    if exit_code in no_raise:
        exit_code = ExitCode.EXPECTED_EXIT
    sys.exit(exit_code)


commitizen_debug_excepthook = partial(commitizen_excepthook, debug=True)

sys.excepthook = commitizen_excepthook


def parse_no_raise(comma_separated_no_raise: str) -> list[int]:
    """Convert the given string to exit codes.

    Receives digits and strings and outputs the parsed integer which
    represents the exit code found in exceptions.
    """

    def exit_code_from_str_or_skip(s: str) -> ExitCode | None:
        try:
            return ExitCode.from_str(s)
        except (KeyError, ValueError):
            out.warn(f"WARN: no_raise value `{s}` is not a valid exit code. Skipping.")
            return None

    return [
        code.value
        for s in comma_separated_no_raise.split(",")
        if (code := exit_code_from_str_or_skip(s)) is not None
    ]


if TYPE_CHECKING:

    class MainCliArgs(argparse.Namespace):
        config: str | None = None  # filepath to the config file
        debug: bool = False
        name: str | None = None
        no_raise: str | None = None  # comma-separated string, later parsed as list[int]
        report: bool = False
        project: bool = False
        commitizen: bool = False
        verbose: bool = False
        func: type[
            commands.Init  # init
            | commands.Commit  # commit (c)
            | commands.ListCz  # ls
            | commands.Example  # example
            | commands.Info  # info
            | commands.Schema  # schema
            | commands.Bump  # bump
            | commands.Changelog  # changelog (ch)
            | commands.Check  # check
            | commands.Version  # version
        ]


def main() -> None:
    parser: argparse.ArgumentParser = get_parser()
    argcomplete.autocomplete(parser)
    # Show help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        raise ExpectedExit()

    # This is for the command required constraint in 2.0
    try:
        args, unknown_args = parser.parse_known_args()
    except SystemExit as e:
        if e.code == 2:
            raise NoCommandFoundError()
        raise e

    args = cast("MainCliArgs", args)
    arguments = vars(args)
    if unknown_args:
        # Raise error for extra-args without -- separation
        if "--" not in unknown_args:
            raise InvalidCommandArgumentError(
                f"Invalid commitizen arguments were found: `{' '.join(unknown_args)}`. "
                "Please use -- separator for extra git args"
            )
        # Raise error for extra-args before --
        elif unknown_args[0] != "--":
            pos = unknown_args.index("--")
            raise InvalidCommandArgumentError(
                f"Invalid commitizen arguments were found before -- separator: `{' '.join(unknown_args[:pos])}`. "
            )
        # Log warning for -- without any extra args
        elif len(unknown_args) == 1:
            logger.warning(
                "\nWARN: Incomplete commit command: received -- separator without any following git arguments\n"
            )
        extra_args = " ".join(unknown_args[1:])
        arguments["extra_cli_args"] = extra_args

    conf = config.read_cfg(args.config)
    if args.name:
        conf.update({"name": args.name})
    elif not conf.path:
        conf.update({"name": "cz_conventional_commits"})

    if args.debug:
        logging.getLogger("commitizen").setLevel(logging.DEBUG)
        sys.excepthook = commitizen_debug_excepthook
    elif args.no_raise:
        no_raise_exit_codes = parse_no_raise(args.no_raise)
        no_raise_debug_excepthook = partial(
            commitizen_excepthook, no_raise=no_raise_exit_codes
        )
        sys.excepthook = no_raise_debug_excepthook

    args.func(conf, arguments)()  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
