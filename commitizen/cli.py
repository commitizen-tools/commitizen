import logging
import argparse
from commitizen import commiter, registered


def get_parser():
    description = (
        'Python cli tool to generate conventional commits.\n'
        'For more information about the topic go to '
        'https://conventionalcommits.org/'
    )

    formater = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog='commitizen',
                                     description=description,
                                     formatter_class=formater)
    parser.set_defaults(func=commiter().run)
    parser.add_argument('--debug', action='store_true', default=False)
    subparser = parser.add_subparsers(title='commands')
    # subparser.add_argument('--debug', default=False)

    example = subparser.add_parser('all')
    example.set_defaults(func=registered)

    example = subparser.add_parser('example')
    example.set_defaults(func=commiter().show_example)

    schema = subparser.add_parser('schema')
    schema.set_defaults(func=commiter().show_schema)

    info = subparser.add_parser('info')
    info.set_defaults(func=commiter().show_info)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.debug:
        logging.getLogger('commitizen').setLevel(logging.DEBUG)
    args.func(args)
