=============
Commitizen
=============

    Python 3 command line utility to standardize commit messages


.. image:: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square
    :alt: Conventional Commits
    :target: https://conventionalcommits.org

.. image:: https://img.shields.io/pypi/v/commitizen.svg?style=flat-square
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/commitizen/

..  image:: https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square
    :alt: Supported versions
    :target: https://pypi.org/project/commitizen/


.. contents::
    :depth: 2


About
=======

This client tool prompts the user with information about the commit.

Based on `conventional commits <https://conventionalcommits.org/>`_

.. image:: docs/images/example.png
    :alt: Example running commitizen

This is an example of how the git messages history would look like:

::

    docs: improved commitizens tab in readme
    feat(cz): jira smart commits
    refactor(cli): renamed all to ls command
    refactor(cz): renamed angular cz to conventional changelog cz
    feat: info command for angular
    docs(README): added badges
    docs(LICENSE): new one
    docs(README): added about, installation, creating, etc
    chore(bumpversion): configured and added as dev dep
    feat(config): new loads from ~/.cz and working project .cz .cz.cfg and setup.cfg

Commitizens
===========

These are the available commiting styles by default:

* cz_conventional_commits: `conventional commits <https://conventionalcommits.org/>`_
* cz_jira: `jira smart commits <https://confluence.atlassian.com/fisheye/using-smart-commits-298976812.html>`_


The installed ones can be checked with:

::

    cz ls


Installation
=============

::

    pip install commitizen


Commiting
=========

Run in your terminal

::

    cz commit

or the shortcut

::

    cz c


Usage
=====

::

    usage: cz [-h] [--debug] [-n NAME] {ls,commit,c,example,info,schema} ...

    Commitizen is a cli tool to generate conventional commits.
    For more information about the topic go to https://conventionalcommits.org/

    optional arguments:
      -h, --help            show this help message and exit
      --debug               use debug mode
      -n NAME, --name NAME  use the given commitizen

    commands:
      {ls,commit,c,example,info,schema}
        ls                 show available commitizens
        commit (c)          create new commit
        example             show commit example
        info                show information about the cz
        schema              show commit schema


Configuration
==============

You can create in your project folder a file called :code:`.cz`, :code:`.cz.cfg` or in your :code:`setup.cfg`
or if you want to configure the global default in your user's home folder a :code:`.cz` file
with the following information:

::

    [commitizen]
    name = cz_conventional_commits


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

::

    .
    ├── cz_jira.py
    └── setup.py

And that's it, you can install it without uploading to pypi by simply doing
:code:`pip install .` If you feel like it should be part of the repo, create a
PR.

Python 2 support
=================

Support for the old version of python (python 2) is limited, there are some
things that won't work, like aliases of commands, so, to commit run:

::

    cz commit


Todo
====

- [ ] auto changelog integration
- [ ] tests
