import logging
import argparse
from commitizen import commiter, registered, run


def get_parser():
    description = (
        'Commitizen is a python cli tool to generate conventional commits.\n'
        'For more information about the topic go to '
        'https://conventionalcommits.org/'
    )

    formater = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog='cz',
                                     description=description,
                                     formatter_class=formater)
    parser.set_defaults(func=commiter().run)
    parser.add_argument('--debug', action='store_true', default=False,
                        help='use debug mode')
    subparser = parser.add_subparsers(title='commands')
    # subparser.add_argument('--debug', default=False)

    allcz = subparser.add_parser('all', help='show available commitizens')
    allcz.set_defaults(func=registered)

    commit = subparser.add_parser('commit', aliases=['c'],
                                  help='create new commit')
    commit.set_defaults(func=run)
    commit.add_argument('-u', '--use_cz', help='use the given commitizen')

    example = subparser.add_parser('example', help='show commit example')
    example.set_defaults(func=commiter().show_example)

    info = subparser.add_parser('info', help='show information about the cz')
    info.set_defaults(func=commiter().show_info)

    schema = subparser.add_parser('schema', help='show commit schema')
    schema.set_defaults(func=commiter().show_schema)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('commitizen').setLevel(logging.DEBUG)
    args.func(args)
