from __future__ import annotations

import argparse
import logging
import sys
from copy import deepcopy
from functools import partial
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, cast

import argcomplete
from decli import cli

from commitizen import commands, config, out, version_schemes
from commitizen.defaults import DEFAULT_SETTINGS
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
        values: object,
        option_string: str | None = None,
    ) -> None:
        if not isinstance(values, str):
            return

        key, sep, value = values.partition("=")
        if not key or not sep:
            raise InvalidCommandArgumentError(
                f"Option {option_string} expect a key=value format"
            )
        kwargs = getattr(namespace, self.dest, None) or {}
        kwargs[key] = value.strip("'\"")
        setattr(namespace, self.dest, kwargs)


tpl_arguments = (
    {
        "name": ["--template", "-t"],
        "help": (
            "Changelog template file name (relative to the current working directory)."
        ),
    },
    {
        "name": ["--extra", "-e"],
        "action": ParseKwargs,
        "dest": "extras",
        "metavar": "EXTRA",
        "help": "Changelog extra variables (in the form 'key=value').",
    },
)

data = {
    "prog": "cz",
    "description": (
        "Commitizen is a powerful release management tool that helps teams maintain consistent and meaningful commit messages while automating version management.\n"
        "For more information, please visit https://commitizen-tools.github.io/commitizen"
    ),
    "formatter_class": argparse.RawDescriptionHelpFormatter,
    "arguments": [
        {
            "name": "--config",
            "help": "The path to the configuration file.",
        },
        {"name": "--debug", "action": "store_true", "help": "Use debug mode."},
        {
            "name": ["-n", "--name"],
            "help": "Use the given commitizen (default: cz_conventional_commits).",
        },
        {
            "name": ["-nr", "--no-raise"],
            "type": str,
            "required": False,
            "help": "Comma-separated error codes that won't raise error, e.g., cz -nr 1,2,3 bump. See codes at https://commitizen-tools.github.io/commitizen/exit_codes/",
        },
    ],
    "subcommands": {
        "title": "commands",
        "required": True,
        "commands": [
            {
                "name": ["init"],
                "description": "Initialize commitizen configuration",
                "help": "Initialize commitizen configuration.",
                "func": commands.Init,
            },
            {
                "name": ["commit", "c"],
                "description": "Create new commit",
                "help": "Create new commit.",
                "func": commands.Commit,
                "arguments": [
                    {
                        "name": ["--retry"],
                        "action": "store_true",
                        "help": "Retry the last commit.",
                    },
                    {
                        "name": ["--no-retry"],
                        "action": "store_true",
                        "default": False,
                        "help": "Skip retry if --retry or `retry_after_failure` is set to true.",
                    },
                    {
                        "name": "--dry-run",
                        "action": "store_true",
                        "help": "Perform a dry run, without committing or modifying files.",
                    },
                    {
                        "name": "--write-message-to-file",
                        "type": Path,
                        "metavar": "FILE_PATH",
                        "help": "Write message to FILE_PATH before committing (can be used with --dry-run).",
                    },
                    {
                        "name": ["-s", "--signoff"],
                        "action": "store_true",
                        "help": "Deprecated, use `cz commit -- -s` instead.",
                    },
                    {
                        "name": ["-a", "--all"],
                        "action": "store_true",
                        # The help text aligns with the description of git commit --all
                        "help": "Automatically stage files that have been modified and deleted, but new files you have not told Git about are not affected.",
                    },
                    {
                        "name": ["-e", "--edit"],
                        "action": "store_true",
                        "default": False,
                        "help": "Edit the commit message before committing.",
                    },
                    {
                        "name": ["-l", "--message-length-limit"],
                        "type": int,
                        "help": "Set the length limit of the commit message; 0 for no limit.",
                    },
                    {
                        "name": ["--"],
                        "action": "store_true",
                        "dest": "double_dash",
                        "help": "Positional arguments separator (recommended).",
                    },
                ],
            },
            {
                "name": "ls",
                "description": "Show available Commitizens",
                "help": "Show available Commitizens.",
                "func": commands.ListCz,
            },
            {
                "name": "example",
                "description": "Show commit example",
                "help": "Show commit example.",
                "func": commands.Example,
            },
            {
                "name": "info",
                "description": "Show information about the cz",
                "help": "Show information about the cz.",
                "func": commands.Info,
            },
            {
                "name": "schema",
                "description": "Show commit schema",
                "help": "Show commit schema.",
                "func": commands.Schema,
            },
            {
                "name": "bump",
                "description": "Bump semantic version based on the git log",
                "help": "Bump semantic version based on the git log.",
                "func": commands.Bump,
                "arguments": [
                    {
                        "name": "--dry-run",
                        "action": "store_true",
                        "help": "Perform a dry run, without committing or modifying files.",
                    },
                    {
                        "name": "--files-only",  # TODO: rename to --version-files-only
                        "action": "store_true",
                        "help": "Bump version in the `version_files` specified in the configuration file only(deprecated; use --version-files-only instead).",
                    },
                    {
                        "name": "--version-files-only",
                        "action": "store_true",
                        "help": "Bump version in the files from the config",
                    },
                    {
                        "name": "--local-version",
                        "action": "store_true",
                        "help": "Bump version only the local version portion (ignoring the public version).",
                    },
                    {
                        "name": ["--changelog", "-ch"],
                        "action": "store_true",
                        "default": False,
                        "help": "Generate the changelog for the latest version.",
                    },
                    {
                        "name": ["--no-verify"],
                        "action": "store_true",
                        "default": False,
                        # The help text aligns with the description of git commit --no-verify
                        "help": "Bypass the pre-commit and commit-msg hooks.",
                    },
                    {
                        "name": "--yes",
                        "action": "store_true",
                        "help": "Accept automatically answered questions.",
                    },
                    {
                        "name": "--tag-format",
                        "help": (
                            "The format used to tag the commit and read it. "
                            "Use it in existing projects, and wrap around simple quotes."
                        ),
                    },
                    {
                        "name": "--bump-message",
                        "help": (
                            "Template used to create the release commit, useful when working with CI."
                        ),
                    },
                    {
                        "name": ["--prerelease", "-pr"],
                        "help": "Type of prerelease.",
                        "choices": ["alpha", "beta", "rc"],
                    },
                    {
                        "name": ["--devrelease", "-d"],
                        "help": "Specify non-negative integer for dev release.",
                        "type": int,
                    },
                    {
                        "name": ["--increment"],
                        "help": "Specify the desired increment.",
                        "choices": ["MAJOR", "MINOR", "PATCH"],
                        "type": str.upper,
                    },
                    {
                        "name": ["--increment-mode"],
                        "choices": ["linear", "exact"],
                        "default": "linear",
                        "help": (
                            "Set the method by which the new version is chosen. "
                            "'linear' (default) resolves the next version based on typical linear version progression, "
                            "where bumping of a pre-release with lower precedence than the current pre-release "
                            "phase maintains the current phase of higher precedence. "
                            "'exact' applies the changes that have been specified (or determined from the commit log) "
                            "without interpretation, ensuring the increment and pre-release are always honored."
                        ),
                    },
                    {
                        "name": ["--check-consistency", "-cc"],
                        "help": (
                            "Check consistency among versions defined in Commitizen configuration file and `version_files`."
                        ),
                        "action": "store_true",
                    },
                    {
                        "name": ["--annotated-tag", "-at"],
                        "help": "Create annotated tag instead of lightweight one.",
                        "action": "store_true",
                    },
                    {
                        "name": ["--annotated-tag-message", "-atm"],
                        "help": "Create annotated tag message.",
                        "type": str,
                    },
                    {
                        "name": ["--gpg-sign", "-s"],
                        "help": "Sign tag instead of lightweight one.",
                        "default": False,
                        "action": "store_true",
                    },
                    {
                        "name": ["--changelog-to-stdout"],
                        "action": "store_true",
                        "default": False,
                        "help": "Output changelog to stdout.",
                    },
                    {
                        "name": ["--git-output-to-stderr"],
                        "action": "store_true",
                        "default": False,
                        "help": "Redirect git output to stderr.",
                    },
                    {
                        "name": ["--retry"],
                        "action": "store_true",
                        "default": False,
                        "help": "Retry commit if it fails for the first time.",
                    },
                    {
                        "name": ["--major-version-zero"],
                        "action": "store_true",
                        "default": None,
                        "help": "Keep major version at zero, even for breaking changes.",
                    },
                    *deepcopy(tpl_arguments),
                    {
                        "name": "--file-name",
                        "help": "File name of changelog (default: 'CHANGELOG.md').",
                    },
                    {
                        "name": ["--prerelease-offset"],
                        "type": int,
                        "default": None,
                        "help": "Start pre-releases with this offset.",
                    },
                    {
                        "name": ["--version-scheme"],
                        "help": "Choose version scheme.",
                        "default": None,
                        "choices": version_schemes.KNOWN_SCHEMES,
                    },
                    {
                        "name": ["--version-type"],
                        "help": "Deprecated, use `--version-scheme` instead.",
                        "default": None,
                        "choices": version_schemes.KNOWN_SCHEMES,
                    },
                    {
                        "name": "manual_version",
                        "type": str,
                        "nargs": "?",
                        "help": "Bump to the given version (e.g., 1.5.3).",
                        "metavar": "MANUAL_VERSION",
                    },
                    {
                        "name": ["--build-metadata"],
                        "help": "Add additional build-metadata to the version-number.",
                        "default": None,
                    },
                    {
                        "name": ["--get-next"],
                        "action": "store_true",
                        "help": "Determine the next version and write to stdout.",
                        "default": False,
                    },
                    {
                        "name": ["--allow-no-commit"],
                        "default": False,
                        "help": "Bump version without eligible commits.",
                        "action": "store_true",
                    },
                ],
            },
            {
                "name": ["changelog", "ch"],
                "description": (
                    "Generate changelog (note that it will overwrite existing files)"
                ),
                "help": (
                    "Generate changelog (note that it will overwrite existing files)."
                ),
                "func": commands.Changelog,
                "arguments": [
                    {
                        "name": "--dry-run",
                        "action": "store_true",
                        "default": False,
                        "help": "Show changelog to stdout.",
                    },
                    {
                        "name": "--file-name",
                        "help": "File name of changelog (default: 'CHANGELOG.md').",
                    },
                    {
                        "name": "--unreleased-version",
                        "help": (
                            "Set the value for the new version (use the tag value), "
                            "instead of using unreleased versions."
                        ),
                    },
                    {
                        "name": "--incremental",
                        "action": "store_true",
                        "default": False,
                        "help": (
                            "Generate changelog from the last created version, "
                            "useful if the changelog has been manually modified."
                        ),
                    },
                    {
                        "name": "rev_range",
                        "type": str,
                        "nargs": "?",
                        "help": "Generate changelog for the given version (e.g., 1.5.3) or version range (e.g., 1.5.3..1.7.9).",
                    },
                    {
                        "name": "--start-rev",
                        "default": None,
                        "help": (
                            "Start rev of the changelog. "
                            "If not set, it will generate changelog from the beginning."
                        ),
                    },
                    {
                        "name": "--merge-prerelease",
                        "action": "store_true",
                        "default": False,
                        "help": (
                            "Collect all changes from prereleases into the next non-prerelease. "
                            "If not set, it will include prereleases in the changelog."
                        ),
                    },
                    {
                        "name": ["--version-scheme"],
                        "help": "Choose version scheme.",
                        "default": None,
                        "choices": version_schemes.KNOWN_SCHEMES,
                    },
                    {
                        "name": "--export-template",
                        "default": None,
                        "help": "Export the changelog template into this file instead of rendering it.",
                    },
                    *deepcopy(tpl_arguments),
                    {
                        "name": "--tag-format",
                        "help": "The format of the tag, wrap around simple quotes.",
                    },
                ],
            },
            {
                "name": ["check"],
                "description": "Validate that a commit message matches the commitizen schema",
                "help": "Validate that a commit message matches the commitizen schema.",
                "func": commands.Check,
                "arguments": [
                    {
                        "name": "--commit-msg-file",
                        "help": (
                            "Ask for the name of the temporary file that contains the commit message. "
                            "Use it in a git hook script: MSG_FILE=$1."
                        ),
                        "exclusive_group": "group1",
                    },
                    {
                        "name": "--rev-range",
                        "help": "Validate the commits in the given range of git rev, e.g., master..HEAD.",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-d", "--use-default-range"],
                        "action": "store_true",
                        "default": False,
                        "help": "Validate the commits from the default branch to HEAD, e.g., refs/remotes/origin/master..HEAD.",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-m", "--message"],
                        "help": "Validate the given commit message.",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["--allow-abort"],
                        "action": "store_true",
                        "default": False,
                        "help": "Allow empty commit messages, which typically abort a commit.",
                    },
                    {
                        "name": ["--allowed-prefixes"],
                        "nargs": "*",
                        "help": "Skip validation for commit messages that start with the specified prefixes.",
                    },
                    {
                        "name": ["-l", "--message-length-limit"],
                        "type": int,
                        "help": "Restrict the length of the **first line** of the commit message; 0 for no limit.",
                    },
                ],
            },
            {
                "name": ["version"],
                "description": (
                    "Get the version of the installed commitizen or the current project (default: installed commitizen)"
                ),
                "help": (
                    "Get the version of the installed commitizen or the current project (default: installed commitizen)."
                ),
                "func": commands.Version,
                "arguments": [
                    {
                        "name": ["-r", "--report"],
                        "help": "Output the system information for reporting bugs.",
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-p", "--project"],
                        "help": "Output the version of the current project.",
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-c", "--commitizen"],
                        "help": "Output the version of the installed commitizen.",
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["-v", "--verbose"],
                        "help": (
                            "Output the version of both the installed commitizen and the current project."
                        ),
                        "action": "store_true",
                        "exclusive_group": "group1",
                    },
                    {
                        "name": ["--major"],
                        "help": "Output just the major version. Must be used with --project or --verbose.",
                        "action": "store_true",
                        "exclusive_group": "group2",
                    },
                    {
                        "name": ["--minor"],
                        "help": "Output just the minor version. Must be used with --project or --verbose.",
                        "action": "store_true",
                        "exclusive_group": "group2",
                    },
                    {
                        "name": ["--tag"],
                        "help": "get the version with tag prefix. Need to be used with --project or --verbose.",
                        "action": "store_true",
                        "exclusive_group": "group2",
                    },
                ],
            },
        ],
    },
}


def commitizen_excepthook(
    exctype: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
    debug: bool = False,
    no_raise: list[int] | None = None,
) -> None:
    traceback = traceback if isinstance(traceback, TracebackType) else None
    if not isinstance(value, CommitizenException):
        sys.__excepthook__(exctype, value, traceback)
        return

    if value.message:
        value.output_method(value.message)
    if debug:
        sys.__excepthook__(exctype, value, traceback)
    exit_code = value.exit_code
    if no_raise is not None and exit_code in no_raise:
        sys.exit(ExitCode.EXPECTED_EXIT)
    sys.exit(exit_code)


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

    class Args(argparse.Namespace):
        config: str | None = None
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
    sys.excepthook = commitizen_excepthook

    parser: argparse.ArgumentParser = cli(data)
    argcomplete.autocomplete(parser)
    # Show help if no arg provided
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
    args = cast("Args", args)
    if args.name:
        conf.update({"name": args.name})
    elif not conf.path:
        conf.update({"name": DEFAULT_SETTINGS["name"]})

    if args.debug:
        logging.getLogger("commitizen").setLevel(logging.DEBUG)
        sys.excepthook = partial(sys.excepthook, debug=True)
    if args.no_raise:
        sys.excepthook = partial(sys.excepthook, no_raise=parse_no_raise(args.no_raise))

    args.func(conf, arguments)()  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
