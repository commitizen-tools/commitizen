import argparse
import logging
import sys
import warnings

from decli import cli

from commitizen import commands, config, out

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
        {
            "name": ["-n", "--name"],
            "help": "use the given commitizen (default: cz_conventional_commits)",
        },
        {
            "name": ["--version"],
            "action": "store_true",
            "help": "get the version of the installed commitizen",
        },
    ],
    "subcommands": {
        "title": "commands",
        # TODO: Add this constraint back in 2.0
        # "required": True,
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
                ],
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
            {
                "name": ["version"],
                "help": (
                    "get the version of the installed commitizen or the current project"
                    " (default: installed commitizen)"
                ),
                "func": commands.Version,
                "arguments": [
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
                ],
            },
            {
                "name": ["init"],
                "help": "init commitizen configuration",
                "func": commands.Init,
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

    # This is for the command required constraint in 2.0
    try:
        args = parser.parse_args()
    except TypeError:
        out.error("Command is required")
        raise SystemExit()

    if args.name:
        conf.update({"name": args.name})
    elif not args.name and not conf.path:
        conf.update({"name": "cz_conventional_commits"})

    if args.version:
        warnings.warn(
            "'cz --version' will be deprecated in next major version. "
            "Please use 'cz version' command from your scripts"
        )
        args.func = commands.Version

    if args.debug:
        warnings.warn(
            "Debug will be deprecated in next major version. "
            "Please remove it from your scripts"
        )
        logging.getLogger("commitizen").setLevel(logging.DEBUG)

    # TODO: This try block can be removed after command is required in 2.0
    # Handle the case that argument is given, but no command is provided
    try:
        args.func(conf, vars(args))()
    except AttributeError:
        out.error("Command is required")
        raise SystemExit()
