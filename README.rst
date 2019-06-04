=============
Commitizen
=============

    Python 3 command line utility to standardize commit messages and bump version


.. image:: https://img.shields.io/travis/Woile/commitizen.svg?style=flat-square
    :alt: Travis
    :target: https://travis-ci.org/Woile/commitizen

.. image:: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square
    :alt: Conventional Commits
    :target: https://conventionalcommits.org

.. image:: https://img.shields.io/pypi/v/commitizen.svg?style=flat-square
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/commitizen/

..  image:: https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square
    :alt: Supported versions
    :target: https://pypi.org/project/commitizen/

.. image:: https://img.shields.io/codecov/c/github/Woile/commitizen.svg?style=flat-square
    :alt: Codecov
    :target: https://codecov.io/gh/Woile/commitizen

.. image:: docs/images/demo.gif
    :alt: Example running commitizen

--------------

**Documentation**: https://Woile.github.io/commitizen/

--------------

.. contents::
    :depth: 2


About
==========

Commitizen is a tool designed for teams.

Its main purpose is to define a standard way of commiting rules
and communicating it (using the cli provided by commitizen).

The reasoning behind it is that is easier to read, and enforces writing
descriptive commits.

Besides that, having a convetion on your commits, makes it possible to
parse them and use them for something else, like generating automatically
the version or a changelog.


Installation
=============

::

    pip install -U commitizen

::

    poetry add commitizen --dev


**Global installation**

::

    sudo pip3 install -U commitizen

Features
========

- Command line utility to create commits with your rules. Defaults: `conventional commits`_
- Display information about your commit rules (commands: schema, example, info)
- Bump version automatically using semantic verisoning based on the commits. `Read More <./docs/bump.md>`_
- Generate a changelog using "Keep a changelog" (Planned feature)


Commit rules
============

This client tool prompts the user with information about the commit.

Based on `conventional commits`_

This is an example of how the git messages history would look like:

::

    fix: minor typos in code
    feat: new command update
    docs: improved commitizens tab in readme
    feat(cz): jira smart commits
    refactor(cli): renamed all to ls command
    feat: info command for angular
    docs(README): added badges
    docs(README): added about, installation, creating, etc
    feat(config): new loads from ~/.cz and working project .cz .cz.cfg and setup.cfg

And then using ``cz bump`` you can change the version of your project

``feat`` to ``MINOR``
``fix`` to ``PATCH``


Commitizens
===========

These are the available commiting styles by default:

* cz_conventional_commits: `conventional commits`_
* cz_jira: `jira smart commits <https://confluence.atlassian.com/fisheye/using-smart-commits-298976812.html>`_


The installed ones can be checked with:

::

    cz ls



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

    $ cz --help
    usage: cz [-h] [--debug] [-n NAME] [--version]
            {ls,commit,c,example,info,schema,bump} ...

    Commitizen is a cli tool to generate conventional commits.
    For more information about the topic go to https://conventionalcommits.org/

    optional arguments:
    -h, --help            show this help message and exit
    --debug               use debug mode
    -n NAME, --name NAME  use the given commitizen
    --version             get the version of the installed commitizen

    commands:
    {ls,commit,c,example,info,schema,bump}
        ls                  show available commitizens
        commit (c)          create new commit
        example             show commit example
        info                show information about the cz
        schema              show commit schema
        bump                bump semantic version based on the git log

Contributing
============

Feel free to create a PR.

1. Clone the repo.
2. Add your modifications
3. Create a virtualenv
4. Run :code:`./scripts/test`


.. _conventional commits: https://conventionalcommits.org/