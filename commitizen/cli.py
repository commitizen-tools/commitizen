import io
import os
import sys
import logging
import argparse
import warnings
from decli import cli
from pathlib import Path
from configparser import RawConfigParser, NoSectionError
from commitizen import defaults, commands, out, config
from commitizen.__version__ import __version__


logger = logging.getLogger(__name__)
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
        {"name": ["-n", "--name"], "help": "use the given commitizen"},
        {
            "name": ["--version"],
            "action": "store_true",
            "help": "get the version of the installed commitizen",
        },
    ],
    "subcommands": {
        "title": "commands",
        "commands": [
            {
                "name": "ls",
                "help": "show available commitizens",
                "func": commands.ListCz,
            },
            {
                "name": ["commit", "c"],
                "help": "create new commit",
                "func": commands.Commit,
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
                        "name": "--yes",
                        "action": "store_true",
                        "help": "accept automatically questions done",
                    },
                    {
                        "name": "--tag-format",
                        "help": (
                            "format used to tag the commmit and read it, "
                            "use it in existing projects, "
                            "wrap around simple quotes"
                        ),
                    },
                    {
                        "name": "--bump-message",
                        "help": (
                            "template used to create the release commmit, "
                            "useful when working with CI"
                        ),
                    },
                    {
                        "name": ["--prerelease", "-pr"],
                        "help": "choose type of prerelease",
                        "choices": ["alpha", "beta", "rc"],
                    },
                    {
                        "name": ["--increment"],
                        "help": "manually specify the desired increment",
                        "choices": ["MAJOR", "MINOR", "PATCH"],
                    },
                ],
            },
        ],
    },
}


def main():
    conf = config.read_cfg()
    parser = cli(data)

    # Show help if no arg provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        raise SystemExit()

    args = parser.parse_args()

    if args.name:
        conf.update({"name": args.name})

    if args.debug:
        warnings.warn(
            "Debug will be deprecated in next major version. "
            "Please remove it from your scripts"
        )
        logging.getLogger("commitizen").setLevel(logging.DEBUG)

    if args.version:
        out.line(__version__)
        raise SystemExit()

    args.func(conf, vars(args))()
