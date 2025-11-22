import argparse
from copy import deepcopy
from pathlib import Path

from decli import cli

from commitizen import commands, version_schemes
from commitizen.exceptions import InvalidCommandArgumentError


class _ParseKwargs(argparse.Action):
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


_TPL_ARGUMENTS = (
    {
        "name": ["--template", "-t"],
        "help": (
            "changelog template file name (relative to the current working directory)"
        ),
    },
    {
        "name": ["--extra", "-e"],
        "action": _ParseKwargs,
        "dest": "extras",
        "metavar": "EXTRA",
        "help": "a changelog extra variable (in the form 'key=value')",
    },
)

_CLI_DATA = {
    "prog": "cz",
    "description": (
        "Commitizen is a powerful release management tool that helps teams maintain consistent and meaningful commit messages while automating version management.\n"
        "For more information, please visit https://commitizen-tools.github.io/commitizen"
    ),
    "formatter_class": argparse.RawDescriptionHelpFormatter,
    "arguments": [
        {
            "name": "--config",
            "help": "the path of configuration file",
        },
        {"name": "--debug", "action": "store_true", "help": "use debug mode"},
        {
            "name": ["-n", "--name"],
            "help": "use the given commitizen (default: cz_conventional_commits)",
        },
        {
            "name": ["-nr", "--no-raise"],
            "type": str,
            "required": False,
            "help": "comma separated error codes that won't raise error, e.g: cz -nr 1,2,3 bump. See codes at https://commitizen-tools.github.io/commitizen/exit_codes/",
        },
    ],
    "subcommands": {
        "title": "commands",
        "required": True,
        "commands": [
            {
                "name": ["init"],
                "description": "init commitizen configuration",
                "help": "init commitizen configuration",
                "func": commands.Init,
            },
            {
                "name": ["commit", "c"],
                "description": "create new commit",
                "help": "create new commit",
                "func": commands.Commit,
                "arguments": [
                    {
                        "name": ["--retry"],
                        "action": "store_true",
                        "help": "retry last commit",
                    },
                    {
                        "name": ["--no-retry"],
                        "action": "store_true",
                        "default": False,
                        "help": "skip retry if retry_after_failure is set to true",
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
                        "help": "Deprecated, use 'cz commit -- -s' instead",
                    },
                    {
                        "name": ["-a", "--all"],
                        "action": "store_true",
                        "help": "Tell the command to automatically stage files that have been modified and deleted, but new files you have not told Git about are not affected.",
                    },
                    {
                        "name": ["-e", "--edit"],
                        "action": "store_true",
                        "default": False,
                        "help": "edit the commit message before committing",
                    },
                    {
                        "name": ["-l", "--message-length-limit"],
                        "type": int,
                        "help": "length limit of the commit message; 0 for no limit",
                    },
                    {
                        "name": ["--"],
                        "action": "store_true",
                        "dest": "double_dash",
                        "help": "Positional arguments separator (recommended)",
                    },
                ],
            },
            {
                "name": "ls",
                "description": "show available commitizens",
                "help": "show available commitizens",
                "func": commands.ListCz,
            },
            {
                "name": "example",
                "description": "show commit example",
                "help": "show commit example",
                "func": commands.Example,
            },
            {
                "name": "info",
                "description": "show information about the cz",
                "help": "show information about the cz",
                "func": commands.Info,
            },
            {
                "name": "schema",
                "description": "show commit schema",
                "help": "show commit schema",
                "func": commands.Schema,
            },
            {
                "name": "bump",
                "description": "bump semantic version based on the git log",
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
                        "name": ["--increment-mode"],
                        "choices": ["linear", "exact"],
                        "default": "linear",
                        "help": (
                            "set the method by which the new version is chosen. "
                            "'linear' (default) guesses the next version based on typical linear version progression, "
                            "such that bumping of a pre-release with lower precedence than the current pre-release "
                            "phase maintains the current phase of higher precedence. "
                            "'exact' applies the changes that have been specified (or determined from the commit log) "
                            "without interpretation, such that the increment and pre-release are always honored"
                        ),
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
                        "name": ["--annotated-tag-message", "-atm"],
                        "help": "create annotated tag message",
                        "type": str,
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
                    *deepcopy(_TPL_ARGUMENTS),
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
                        "help": "Deprecated, use --version-scheme instead",
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
                    {
                        "name": ["--build-metadata"],
                        "help": "Add additional build-metadata to the version-number",
                        "default": None,
                    },
                    {
                        "name": ["--get-next"],
                        "action": "store_true",
                        "help": "Determine the next version and write to stdout",
                        "default": False,
                    },
                    {
                        "name": ["--allow-no-commit"],
                        "default": False,
                        "help": "bump version without eligible commits",
                        "action": "store_true",
                    },
                ],
            },
            {
                "name": ["changelog", "ch"],
                "description": (
                    "generate changelog (note that it will overwrite existing file)"
                ),
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
                    *deepcopy(_TPL_ARGUMENTS),
                    {
                        "name": "--tag-format",
                        "help": "The format of the tag, wrap around simple quotes",
                    },
                ],
            },
            {
                "name": ["check"],
                "description": "validates that a commit message matches the commitizen schema",
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
                        "name": ["-d", "--use-default-range"],
                        "action": "store_true",
                        "default": False,
                        "help": "check from the default branch to HEAD. e.g, refs/remotes/origin/master..HEAD",
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
                    {
                        "name": ["-l", "--message-length-limit"],
                        "type": int,
                        "help": "length limit of the commit message; 0 for no limit",
                    },
                ],
            },
            {
                "name": ["version"],
                "description": (
                    "get the version of the installed commitizen or the current project"
                    " (default: installed commitizen)"
                ),
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
                    {
                        "name": ["--major"],
                        "help": "get just the major version",
                        "action": "store_true",
                        "exclusive_group": "group2",
                    },
                    {
                        "name": ["--minor"],
                        "help": "get just the minor version",
                        "action": "store_true",
                        "exclusive_group": "group2",
                    },
                ],
            },
        ],
    },
}


def get_parser() -> argparse.ArgumentParser:
    return cli(_CLI_DATA)
