import os
from commitizen.cz.cz_base import BaseCommitizen


__all__ = ['ConventionalCommitsCz']


def parse_scope(text=None):
    if text is None:
        return None
    text = text.strip().title().split()
    text[0] = text[0].lower()
    return ''.join(text)


class ConventionalCommitsCz(BaseCommitizen):

    def questions(self):
        questions = [
            {
                'type': 'list',
                'name': 'prefix',
                'message': 'Select the type of change you are committing',
                'choices': [
                    {
                        'value': 'feat',
                        'name': 'feat: A new feature',
                    },
                    {
                        'value': 'fix',
                        'name': 'fix: A bug fix',
                    },
                    {
                        'value': 'docs',
                        'name': 'docs: Documentation only changes',
                    },
                    {
                        'value': 'style',
                        'name': ('style: Changes that do not affect the '
                                 'meaning of the code (white-space, formatting,'
                                 ' missing semi-colons, etc)'),
                    },
                    {
                        'value': 'refactor',
                        'name': ('refactor: A code change that neither fixes '
                                 'a bug nor adds a feature')
                    },
                    {
                        'value': 'perf',
                        'name': 'perf: A code change that improves performance',
                    },
                    {
                        'value': 'test',
                        'name': ('test: Adding missing or correcting '
                                 'existing tests')
                    },
                    {
                        'value': 'chore',
                        'name': ('chore: Changes to the build process or '
                                 'auxiliary tools and libraries such as '
                                 'documentation generation'),
                    },
                ]
            },
            {
                'type': 'input',
                'name': 'scope',
                'message': ('Scope. Could be anything specifying place of the '
                            'commit change (users, db, poll):\n')
            },
            {
                'type': 'input',
                'name': 'subject',
                'message': ('Subject. Concise description of the changes. '
                            'Imperative, lower case and no final dot:\n')
            },
            {
                'type': 'input',
                'name': 'body',
                'message': ('Body. Motivation for the change and contrast this '
                            'with previous behavior:\n')
            },
            {
                'type': 'input',
                'name': 'footer',
                'message': ('Footer. Information about Breaking Changes and '
                            'reference issues that this commit closes:\n')
            }
        ]
        return questions

    def message(self, answers):
        prefix = answers['prefix']
        scope = answers['scope']
        subject = answers['subject']
        body = answers['body']
        footer = answers['footer']
        message = ''

        if prefix:
            message += '{0}'.format(prefix.lower().strip('.').strip())
            if scope:
                message += '({0})'.format(parse_scope(scope))
            message += ': '
        if subject:
            message += '{0}'.format(subject.lower().strip('.').strip())
        if body:
            message += '\n\n{0}'.format(body)
        if footer:
            message += '\n\n{0}'.format(footer)
        return message

    def example(self):
        return (
            'feat($injector): ability to load new modules after bootstrapping\n'
            '\nThe new method `$injector.loadNewModules(modules)` will add '
            'each of the\ninjectables to the injector and execute all of the '
            'config and run blocks\nfor each module passed to the method.\n'
            '\nCloses #324'
        )

    def schema(self):
        return ('<type>(<scope>): <subject>\n'
                '<BLANK LINE>\n'
                '<body>\n'
                '<BLANK LINE>\n'
                '<footer>')

    def info(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, 'cz_conventional_commits_info.txt')
        with open(filepath, 'r') as f:
            content = f.read()
        return content
