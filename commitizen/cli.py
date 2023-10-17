from __future__ import annotations

import argparse
import logging
import sys
from copy import deepcopy
from functools import partial
from pathlib import Path
from types import TracebackType
from typing import Any, Sequence

import argcomplete
from decli import cli

from commitizen import commands, config, out, version_schemes
from commitizen.exceptions import (
    CommitizenException,
    ExitCode,
    ExpectedExit,
    InvalidCommandArgumentError,
    NoCommandFoundError,
)

logger = logging.getLogger(__name__)


class ParseKwargs(argparse.Action):
    """
    Parse arguments in the for `key=value`.

    Quoted strings are automatically unquoted.
    Can be submitted multiple times:

    ex:
        -k key=value -k double-quotes="value" -k single-quotes='value'

        will result in

        namespace["opt"] == {
            "key": "value",
            "double-quotes": "value",
            "single-quotes": "value",
        }
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        kwarg: str | Sequence[Any] | None,
        option_string: str | None = None,
    ):
        if not isinstance(kwarg, str):
            return
        if "=" not in kwarg:
            raise InvalidCommandArgumentError(
                f"Option {option_string} expect a key=value format"
            )
        kwargs = getattr(namespace, self.dest, None) or {}
        key, value = kwarg.split("=", 1)
        if not key:
            raise InvalidCommandArgumentError(
                f"Option {option_string} expect a key=value format"
            )
        kwargs[key] = value.strip("'\"")
        setattr(namespace, self.dest, kwargs)


tpl_arguments = (
    {
        "name": ["--template", "-t"],
        "help": (
            "changelog template file name "
            "(relative to the current working directory)"
        ),
    },
    {
        "name": ["--extra", "-e"],
        "action": ParseKwargs,
        "dest": "extras",
        "metavar": "EXTRA",
        "help": "a changelog extra variable (in the form 'key=value')",
    },
)

data = {
    "prog": "cz",
    "description": (
        "Commitizen is a cli tool to generate conventional commits.\n"
        "For more information about the topic go to "
        "https://conventionalcommits.org/"
    ),
    "formatter_class": argparse.RawDescriptionHelpFormatter,
    "arguments": [
        {"name": "--debug", "action": "store_true", "help": "use debug mode"},
        {
            "name": ["-n", "--name"],
            "help": "use the given commitizen (default: cz_conventional_commits)",
        },
        {
            "name": ["-nr", "--no-raise"],
            "type": str,
            "required": False,
            "help": "comma separated error codes that won't rise error, e.g: cz -nr 1,2,3 bump. See codes at https://commitizen-tools.github.io/commitizen/exit_codes/",
        },
    ],
    "subcommands": {
        "title": "commands",
        "required": True,
        "commands": [
            {
                "name": ["init"],
                "help": "init commitizen configuration",
                "func": commands.Init,
            },
            {
                "name": ["commit", "c"],
                "help": "create new commit",
                "func": commands.Commit,
                "arguments": [
                    {
                        "name": ["--retry"],
                        "action": "store_true",
                        "help": "retry last commit",
                    },
                    {
                        "name": "--dry-run",
                        "action": "store_true",
                        "help": "show output to stdout, no commit, no modified files",
                    },
                    {
                        "name": "--write-message-to-file",
                        "type": Path,
                        "metavar": "FILE_PATH",
                        "help": "write message to file before committing (can be combined with --dry-run)",
                    },
                    {
                        "name": ["-s", "--signoff"],
                        "action": "store_true",
                        "help": "sign off the commit",
                    },
                    {
                        "name": ["-a", "--all"],
                        "action": "store_true",
                        "help": "Tell the command to automatically stage files that have been modified and deleted, but new files you have not told Git about are not affected.",
                    },
                ],
            },
            {
                "name": "ls",
                "help": "show available commitizens",
                "func": commands.ListCz,
            },
            {
                "name": "example",
                "help": "show commit example",
                "func": commands.Example,
            },
            {
                "name": "info",
                "help": "show information about the cz",
                "func": commands.Info,
            },
            {"name": "schema", "help": "show commit schema", "func": commands.Schema},
            {
                "name": "bump",
                "help": "bump semantic version based on the git log",
                "func": commands.Bump,
                "arguments": [
                    {
                        "name": "--dry-run",
                        "action": "store_true",
                        "help": "show output to stdout, no commit, no modified files",
                    },
                    {
                        "name": "--files-only",
                        "action": "store_true",
                        "help": "bump version in the files from the config",
                    },
                    {
                        "name": "--local-version",
                        "action": "store_true",
                        "help": "bump only the local version portion",
                    },
                    {
                        "name": ["--changelog", "-ch"],
                        "action": "store_true",
                        "default": False,
                        "help": "generate the changelog for the newest version",
                    },
                    {
                        "name": ["--no-verify"],
                        "action": "store_true",
                        "default": False,
                        "help": "this option bypasses the pre-commit and commit-msg hooks",
                    },
                    {
                        "name": "--yes",
                        "action": "store_true",
                        "help": "accept automatically questions done",
                    },
                    {
                        "name": "--tag-format",
                        "help": (
                            "the format used to tag the commit and read it, "
                            "use it in existing projects, "
                            "wrap around simple quotes"
                        ),
                    },
                    {
                        "name": "--bump-message",
                        "help": (
                            "template used to create the release commit, "
                            "useful when working with CI"
                        ),
                    },
                    {
                        "name": ["--prerelease", "-pr"],
                        "help": "choose type of prerelease",
                        "choices": ["alpha", "beta", "rc"],
                    },
                    {
                        "name": ["--devrelease", "-d"],
                        "help": "specify non-negative integer for dev. release",
                        "type": int,
                    },
                    {
                        "name": ["--increment"],
                        "help": "manually specify the desired increment",
                        "choices": ["MAJOR", "MINOR", "PATCH"],
                        "type": str.upper,
                    },
                    {
                        "name": ["--check-consistency", "-cc"],
                        "help": (
                            "check consistency among versions defined in "
                            "commitizen configuration and version_files"
                        ),
                        "action": "store_true",
                    },
                    {
                        "name": ["--annotated-tag", "-at"],
                        "help": "create annotated tag instead of lightweight one",
                        "action": "store_true",
                    },
                    {
                        "name": ["--gpg-sign", "-s"],
                        "help": "sign tag instead of lightweight one",
                        "default": False,
                        "action": "store_true",
                    },
                    {
                        "name": ["--changelog-to-stdout"],
                        "action": "store_true",
                        "default": False,
                        "help": "Output changelog to the stdout",
                    },
                    {
                        "name": ["--git-output-to-stderr"],
                        "action": "store_true",
                        "default": False,
                        "help": "Redirect git output to stderr",
                    },
                    {
                        "name": ["--retry"],
                        "action": "store_true",
                        "default": False,
                        "help": "retry commit if it fails the 1st time",
                    },
                    {
                        "name": ["--major-version-zero"],
                        "action": "store_true",
                        "default": None,
                        "help": "keep major version at zero, even for breaking changes",
                    },
                    *deepcopy(tpl_arguments),
                    {
                        "name": "--file-name",
                        "help": "file name of changelog (default: 'CHANGELOG.md')",
                    },
                    {
                        "name": ["--prerelease-offset"],
                        "type": int,
                        "default": None,
                        "help": "start pre-releases with this offset",
                    },
                    {
                        "name": ["--version-scheme"],
                        "help": "choose version scheme",
                        "default": None,
                        "choices": version_schemes.KNOWN_SCHEMES,
                    },
                    {
                        "name": ["--version-type"],
                        "help": "Deprecated, use --version-scheme",
                        "default": None,
                        "choices": version_schemes.KNOWN_SCHEMES,
                    },
                    {
                        "name": "manual_version",
                        "type": str,
                        "nargs": "?",
                        "help": "bump to the given version (e.g: 1.5.3)",
                        "metavar": "MANUAL_VERSION",
                    },
                ],
            },
            {
                "name": ["changelog", "ch"],
                "help": (
                    "generate changelog (note that it will overwrite existing file)"
                ),
                "func": commands.Changelog,
                "arguments": [
                    {
                        "name": "--dry-run",
                        "action": "store_true",
                        "default": False,
                        "help": "show changelog to stdout",
                    },
                    {
                        "name": "--file-name",
                        "help": "file name of changelog (default: 'CHANGELOG.md')",
                    },
                    {
                        "name": "--unreleased-version",
                        "help": (
                            "set the value for the new version (use the tag value), "
                            "instead of using unreleased"
                        ),
                    },
                    {
                        "name": "--incremental",
                        "action": "store_true",
                        "default": False,
                        "help": (
                            "generates changelog from last created version, "
                            "useful if the changelog has been manually modified"
                        ),
                    },
                    {
                        "name": "rev_range",
                        "type": str,
                        "nargs": "?",
                        "help": "generates changelog for the given version (e.g: 1.5.3) or version range (e.g: 1.5.3..1.7.9)",
                    },
                    {
                        "name": "--start-rev",
                        "default": None,
                        "help": (
                            "start rev of the changelog. "
                            "If not set, it will generate changelog from the start"
                        ),
                    },
                    {
                        "name": "--merge-prerelease",
                        "action": "store_true",
                        "default": False,
                        "help": (
                            "collect all changes from prereleases into next non-prerelease. "
                            "If not set, it will include prereleases in the changelog"
                        ),
                    },
                    {
                        "name": ["--version-scheme"],
                        "help": "choose version scheme",
                        "default": None,
                        "choices": version_schemes.KNOWN_SCHEMES,
                    },
                    {
                        "name": "--export-template",
                        "default": None,
                        "help": "Export the changelog template into this file instead of rendering it",
                    },
                    *deepcopy(tpl_arguments),
                ],
            },
            {
                "name": ["check"],
                "help": "validates that a commit message matches the commitizen schema",
                "func": commands.Check,
                "arguments": [
                    {
                        "name": "--commit-msg-file",
                        "help": (
                            "ask for the name of the temporal file that contains "
                            "the commit message. "
                            "Using it in a git hook script: MSG_FILE=$1"
                        ),
                        "exclusive_group": "group1",
                    },
                    {
                        "name": "--rev-range",
                        "help": "a range of git rev to check. e.g, master..HEAD",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-m", "--message"],
                        "help": "commit message that needs to be checked",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["--allow-abort"],
                        "action": "store_true",
                        "default": False,
                        "help": "allow empty commit messages, which typically abort a commit",
                    },
                    {
                        "name": ["--allowed-prefixes"],
                        "nargs": "*",
                        "help": "allowed commit message prefixes. "
                        "If the message starts by one of these prefixes, "
                        "the message won't be checked against the regex",
                    },
                ],
            },
            {
                "name": ["version"],
                "help": (
                    "get the version of the installed commitizen or the current project"
                    " (default: installed commitizen)"
                ),
                "func": commands.Version,
                "arguments": [
                    {
                        "name": ["-r", "--report"],
                        "help": "get system information for reporting bugs",
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-p", "--project"],
                        "help": "get the version of the current project",
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-c", "--commitizen"],
                        "help": "get the version of the installed commitizen",
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-v", "--verbose"],
                        "help": (
                            "get the version of both the installed commitizen "
                            "and the current project"
                        ),
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                ],
            },
        ],
    },
}

original_excepthook = sys.excepthook


def commitizen_excepthook(
    type, value, traceback, debug=False, no_raise: list[int] | None = None
):
    traceback = traceback if isinstance(traceback, TracebackType) else None
    if not no_raise:
        no_raise = []
    if isinstance(value, CommitizenException):
        if value.message:
            value.output_method(value.message)
        if debug:
            original_excepthook(type, value, traceback)
        exit_code = value.exit_code
        if exit_code in no_raise:
            exit_code = 0
        sys.exit(exit_code)
    else:
        original_excepthook(type, value, traceback)


commitizen_debug_excepthook = partial(commitizen_excepthook, debug=True)

sys.excepthook = commitizen_excepthook


def parse_no_raise(comma_separated_no_raise: str) -> list[int]:
    """Convert the given string to exit codes.

    Receives digits and strings and outputs the parsed integer which
    represents the exit code found in exceptions.
    """
    no_raise_items: list[str] = comma_separated_no_raise.split(",")
    no_raise_codes = []
    for item in no_raise_items:
        if item.isdecimal():
            no_raise_codes.append(int(item))
            continue
        try:
            exit_code = ExitCode[item.strip()]
        except KeyError:
            out.warn(f"WARN: no_raise key `{item}` does not exist. Skipping.")
            continue
        else:
            no_raise_codes.append(exit_code.value)
    return no_raise_codes


def main():
    conf = config.read_cfg()
    parser = cli(data)

    argcomplete.autocomplete(parser)
    # Show help if no arg provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        raise ExpectedExit()

    # This is for the command required constraint in 2.0
    try:
        args, unknown_args = parser.parse_known_args()
    except (TypeError, SystemExit) as e:
        # https://github.com/commitizen-tools/commitizen/issues/429
        # argparse raises TypeError when non exist command is provided on Python < 3.9
        # but raise SystemExit with exit code == 2 on Python 3.9
        if isinstance(e, TypeError) or (isinstance(e, SystemExit) and e.code == 2):
            raise NoCommandFoundError()
        raise e

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

    if args.name:
        conf.update({"name": args.name})
    elif not args.name and not conf.path:
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

    args.func(conf, arguments)()


if __name__ == "__main__":
    main()
