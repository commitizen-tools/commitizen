## Custom commit rules

Create a file starting with `cz_` for example `cz_jira.py`. This prefix
is used to detect the plugin. Same method [flask uses]

Inherit from `BaseCommitizen` and you must define `questions` and
`message`. The others are optionals.

```python
from commitizen.cz.base import BaseCommitizen

class JiraCz(BaseCommitizen):

    def questions(self) -> list:
        """Questions regarding the commit message."""
        questions = [
            {
                'type': 'input',
                'name': 'title',
                'message': 'Commit title'
            },
            {
                'type': 'input',
                'name': 'issue',
                'message': 'Jira Issue number:'
            },
        ]
        return questions

    def message(self, answers: dict) -> str:
        """Generate the message with the given answers."""
        return '{0} (#{1})'.format(answers['title'], answers['issue'])

    def example(self) -> str:
        """Provide an example to help understand the style (OPTIONAL)

        Used by `cz example`.
        """
        return 'Problem with user (#321)'

    def schema(self) -> str:
        """Show the schema used (OPTIONAL)

        Used by `cz schema`.
        """
        return '<title> (<issue>)'

    def info(self) -> str:
        """Explanation of the commit rules. (OPTIONAL)

        Used by `cz info`.
        """
        return 'We use this because is useful'


discover_this = JiraCz  # used by the plugin system
```

The next file required is `setup.py` modified from flask version

```python
from setuptools import setup

setup(
    name='JiraCommitizen',
    version='0.1.0',
    py_modules=['cz_jira'],
    license='MIT',
    long_description='this is a long description',
    install_requires=['commitizen']
)
```

So at the end we would have

    .
    ├── cz_jira.py
    └── setup.py

And that's it, you can install it without uploading to pypi by simply
doing `pip install .`

If you feel like it should be part of this repo, create a PR.

[flask uses]: http://flask.pocoo.org/docs/0.12/extensiondev/
