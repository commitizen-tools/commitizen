[![Github Actions](https://github.com/Woile/commitizen/workflows/Python%20package/badge.svg?style=flat-square)](https://github.com/Woile/commitizen/actions)
[![Conventional
Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![PyPI Package latest
release](https://img.shields.io/pypi/v/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)
[![Supported
versions](https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)
[![Codecov](https://img.shields.io/codecov/c/github/Woile/commitizen.svg?style=flat-square)](https://codecov.io/gh/Woile/commitizen)

![Using commitizen cli](images/demo.gif)

## About

Commitizen is a tool designed for teams.

Its main purpose is to define a standard way of committing rules
and communicating it (using the cli provided by commitizen).

The reasoning behind it is that it is easier to read, and enforces writing
descriptive commits.

Besides that, having a convention on your commits makes it possible to
parse them and use them for something else, like generating automatically
the version or a changelog.

### Commitizen features

- Command-line utility to create commits with your rules. Defaults: [Conventional commits][conventional_commits]
- Display information about your commit rules (commands: schema, example, info)
- Bump version automatically using [semantic verisoning][semver] based on the commits. [Read More](./bump.md)
- Generate a changelog using [Keep a changelog][keepchangelog] (Planned feature)

## Requirements

Python 3.6+

[Git][gitscm] `1.8.5.2`+

## Installation

Global installation

```bash
sudo pip3 install -U Commitizen
```

### Python project

You can add it to your local project using one of these:

```bash
pip install -U commitizen
```

```bash
poetry add commitizen --dev
```

## Usage

### Commiting

Run in your terminal

```bash
cz commit
```

or the shortcut

```bash
cz c
```

### Help

```bash
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
    version             get the version of the installed commitizen or the
                        current project (default: installed commitizen)
    check               validates that a commit message matches the commitizen schema
    init                init commitizen configuration
```

## Contributing

Feel free to create a PR.

1. Clone the repo.
2. Add your modifications
3. Create a virtualenv
4. Run `./scripts/test`

[conventional_commits]: https://www.conventionalcommits.org
[semver]: https://semver.org/
[keepchangelog]: https://keepachangelog.com/
[gitscm]: https://git-scm.com/downloads
[travis]: https://img.shields.io/travis/Woile/commitizen.svg?style=flat-square
