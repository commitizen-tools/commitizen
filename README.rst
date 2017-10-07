=============
Commitizen
=============

::

    Python 3 command line utility to standardize commit messages

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)


About
=======

This client tool prompts the user with information about the commit.

Based on `conventional commits <https://conventionalcommits.org/>`_

By default it uses `angular guidelines <https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#commit>`_


Installation
=============

    pip install commitizen


Usage
======

Run in your terminal

    cz

Help
=====


    cz --help

Creating a commiter
========================

Create a file starting with :code:`cz_` for example :code:`cz_jira.py`.
This prefix is used to detect the plugin. Same method `flask uses <http://flask.pocoo.org/docs/0.12/extensiondev/>`_

Inherit from :code:`BaseCommitizen` and you must define :code:`questions`
and :code:`message`. The others are optionals.


.. code-block:: python

    from commitizen import BaseCommitizen

    class JiraCz(BaseCommitizen):

        def questions(self):
            """Questions regarding the commit message.

            Must have 'whaaaaat' format.
            More info: https://github.com/finklabs/whaaaaat/

            :rtype: list
            """
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

        def message(self, answers):
            """Generate the message with the given answers.

            :type answers: dict
            :rtype: string
            """
            return '{0} (#{1})'.format(answers['title'], answers['issue'])

        def example(self):
            """Provide an example to help understand the style (OPTIONAL)
            Used by cz example.

            :rtype: string
            """
            return 'Problem with user (#321)'

        def schema(self):
            """Show the schema used (OPTIONAL)

            :rtype: string
            """
            return '<title> (<issue>)'

        def info(self):
            """Explanation of the commit rules. (OPTIONAL)
            :rtype: string
            """
            return 'We use this because is useful'


    discover_this = JiraCz  # used by the plugin system


The next file required is :code:`setup.py` modified from flask version

.. code-block:: python

    from distutils.core import setup

    setup(
        name='JiraCommitizen',
        version='0.1.0',
        py_modules=['cz_jira'],
        license='MIT',
        long_description='this is a long description',
        install_requires=['commitizen']
    )

So at the end we would have

.. code-block::

    .
    ├── cz_jira.py
    └── setup.py

And that's it, you can install it without uploading by doing
:code:`pip install .`


Todo
====

- [ ] auto changelog integration
- [ ] tests
