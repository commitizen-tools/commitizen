import io
import os
import sys
import logging
import argparse
from decli import cli
from pathlib import Path
from configparser import RawConfigParser, NoSectionError
from commitizen.application import Application
from commitizen import deafults


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
            "help": "use the given commitizen",
        },
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
                "func": lambda app: app.detected_cz,
            },
            {
                "name": ["commit", "c"],
                "help": "create new commit",
                "func": lambda app: app.cz.run,
            },
            {
                "name": "example",
                "help": "show commit example",
                "func": lambda app: app.cz.show_example,
            },
            {
                "name": "info",
                "help": "show information about the cz",
                "func": lambda app: app.cz.show_info,
            },
            {
                "name": "schema",
                "help": "show commit schema",
                "func": lambda app: app.cz.show_schema,
            },
        ],
    },
}


def load_cfg():
    settings = {"name": deafults.NAME}
    config = RawConfigParser("")
    home = str(Path.home())

    config_file = ".cz"
    global_cfg = os.path.join(home, config_file)

    # load cfg from current project
    configs = ["setup.cfg", ".cz.cfg", config_file, global_cfg]
    for cfg in configs:
        if not os.path.exists(config_file) and os.path.exists(cfg):
            config_file = cfg

        config_file_exists = os.path.exists(config_file)
        if config_file_exists:
            logger.debug('Reading file "%s"', config_file)
            config.readfp(io.open(config_file, "rt", encoding="utf-8"))
            log_config = io.StringIO()
            config.write(log_config)
            try:
                settings.update(dict(config.items("commitizen")))
                break
            except NoSectionError:
                # The file does not have commitizen section
                continue

    return settings


def main():
    config = load_cfg()
    parser = cli(data)

    # Show help if no arg provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        raise SystemExit(1)

    args = parser.parse_args()
    app = Application(**config)

    if args.name:
        app.name = args.name

    if args.debug:
        logging.getLogger("commitizen").setLevel(logging.DEBUG)

    if args.version:
        logger.info(app.version)
        sys.exit(0)

    args.func(app)(args)
