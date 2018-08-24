import io
import os
import sys
import logging
import argparse
from configparser import RawConfigParser
from commitizen import (
    registered,
    run,
    set_commiter,
    show_example,
    show_info,
    show_schema,
    version,
)


req_version = (3,)
cur_version = sys.version_info
logger = logging.getLogger(__name__)

if cur_version > req_version:
    from pathlib import Path
else:
    from pathlib2 import Path


def get_parser(config):
    description = (
        "Commitizen is a cli tool to generate conventional commits.\n"
        "For more information about the topic go to "
        "https://conventionalcommits.org/"
    )

    formater = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        prog="cz", description=description, formatter_class=formater
    )
    parser.set_defaults(func=run)
    parser.add_argument(
        "--debug", action="store_true", default=False, help="use debug mode"
    )
    parser.add_argument(
        "-n", "--name", default=config.get("name"), help="use the given commitizen"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="get the version of the installed commitizen",
    )

    subparser = parser.add_subparsers(title="commands")

    lscz = subparser.add_parser("ls", help="show available commitizens")
    lscz.set_defaults(func=registered)

    if cur_version > req_version:
        commit = subparser.add_parser("commit", aliases=["c"], help="create new commit")
    else:
        commit = subparser.add_parser("commit", help="create new commit")
        commit = subparser.add_parser("c", help="alias for commit")

    commit.set_defaults(func=run)

    example = subparser.add_parser("example", help="show commit example")
    example.set_defaults(func=show_example)

    info = subparser.add_parser("info", help="show information about the cz")
    info.set_defaults(func=show_info)

    schema = subparser.add_parser("schema", help="show commit schema")
    schema.set_defaults(func=show_schema)

    return parser


def load_cfg():
    defaults = {"name": "cz_conventional_commits"}
    config = RawConfigParser("")
    try:
        home = str(Path.home())
    except AttributeError:
        home = os.path.expanduser("~")

    config_file = ".cz"

    # load cfg from home folder
    global_cfg = os.path.join(home, config_file)
    if os.path.exists(global_cfg):
        config.readfp(io.open(global_cfg, "rt", encoding="utf-8"))
        log_config = io.StringIO()
        config.write(log_config)
        defaults.update(dict(config.items("commitizen")))

    # load cfg from current project
    configs = ["setup.cfg", ".cz.cfg"]
    for cfg in configs:
        if not os.path.exists(config_file) and os.path.exists(cfg):
            config_file = cfg
            break

    config_file_exists = os.path.exists(config_file)
    if config_file_exists:
        logger.debug('Reading file "%s"', config_file)
        config.readfp(io.open(config_file, "rt", encoding="utf-8"))
        log_config = io.StringIO()
        config.write(log_config)
        defaults.update(dict(config.items("commitizen")))

    return defaults


def main():
    config = load_cfg()
    parser = get_parser(config)
    args = parser.parse_args()

    if args.debug:
        logging.getLogger("commitizen").setLevel(logging.DEBUG)

    if args.version:
        logger.info(version())
        sys.exit(0)

    set_commiter(args.name)
    args.func(args)
