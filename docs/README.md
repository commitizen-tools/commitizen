[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/commitizen-tools/commitizen/pythonpackage.yml?label=python%20package&logo=github&logoColor=white&style=flat-square)](https://github.com/commitizen-tools/commitizen/actions)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![PyPI Package latest release](https://img.shields.io/pypi/v/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)
[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/commitizen?style=flat-square)](https://pypi.org/project/commitizen/)
[![Supported versions](https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/commitizen?style=flat-square)](https://anaconda.org/conda-forge/commitizen)
[![homebrew](https://img.shields.io/homebrew/v/commitizen?color=teal&style=flat-square)](https://formulae.brew.sh/formula/commitizen)
[![Codecov](https://img.shields.io/codecov/c/github/commitizen-tools/commitizen.svg?style=flat-square)](https://codecov.io/gh/commitizen-tools/commitizen)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

![Using commitizen cli](images/demo.gif)

---

**Documentation:** [https://commitizen-tools.github.io/commitizen/](https://commitizen-tools.github.io/commitizen/)

---

## About

Commitizen is a powerful release management tool that helps teams maintain consistent and meaningful commit messages while automating version management.

### What Commitizen Does

By enforcing standardized commit conventions (defaulting to [Conventional Commits][conventional_commits]), Commitizen helps teams:

- Write clear, structured commit messages
- Automatically manage version numbers using semantic versioning
- Generate and maintain changelogs
- Streamline the release process

### Key Benefits

With just a simple `cz bump` command, Commitizen handles:

1. **Version Management**: Automatically bumps version numbers and updates version files based on your commit history
2. **Changelog Generation**: Creates and updates changelogs following the [Keep a changelog][keepchangelog] format
3. **Commit Standardization**: Enforces consistent commit message formats across your team

This standardization makes your commit history more readable and meaningful, while the automation reduces manual work and potential errors in the release process.

### Features

- Command-line utility to create commits with your rules. Defaults: [Conventional commits][conventional_commits]
- Bump version automatically using [semantic versioning][semver] based on the commits. [Read More](./commands/bump.md)
- Generate a changelog using [Keep a changelog][keepchangelog]
- Update your project's version files automatically
- Display information about your commit rules (commands: schema, example, info)
- Create your own set of rules and publish them to pip. Read more on [Customization](./customization.md)

## Requirements

[Python](https://www.python.org/downloads/) `3.9+`

[Git][gitscm] `1.8.5.2+`

## Installation

Install commitizen in your system using `pipx` (Recommended, <https://pypa.github.io/pipx/installation/>):

```bash
pipx ensurepath
pipx install commitizen
pipx upgrade commitizen
```

Install commitizen using `pip` with the `--user` flag:

```bash
pip install --user -U commitizen
```

### Python project

You can add it to your local project using one of the following methods.

With `pip`:

```bash
pip install -U commitizen
```

With `conda`:

```bash
conda install -c conda-forge commitizen
```

With Poetry >= 1.2.0:

```bash
poetry add commitizen --group dev
```

With Poetry < 1.2.0:

```bash
poetry add commitizen --dev
```

### macOS

via [homebrew](https://formulae.brew.sh/formula/commitizen):

```bash
brew install commitizen
```

## Usage

Most of the time, this is the only command you'll run:

```sh
cz bump
```

On top of that, you can use commitizen to assist you with the creation of commits:

```sh
cz commit
```

Read more in the section [Getting Started](./getting_started.md).

### Help

<!-- Please manually update the following section after changing `cz --help` command output. -->

```sh
$ cz --help
usage: cz [-h] [--config CONFIG] [--debug] [-n NAME] [-nr NO_RAISE] {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version} ...

Commitizen is a cli tool to generate conventional commits.
For more information about the topic go to https://conventionalcommits.org/

options:
  -h, --help            show this help message and exit
  --config CONFIG       the path of configuration file
  --debug               use debug mode
  -n, --name NAME       use the given commitizen (default: cz_conventional_commits)
  -nr, --no-raise NO_RAISE
                        comma separated error codes that won't raise error, e.g: cz -nr 1,2,3 bump. See codes at https://commitizen-tools.github.io/commitizen/exit_codes/

commands:
  {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version}
    init                init commitizen configuration
    commit (c)          create new commit
    ls                  show available commitizens
    example             show commit example
    info                show information about the cz
    schema              show commit schema
    bump                bump semantic version based on the git log
    changelog (ch)      generate changelog (note that it will overwrite existing file)
    check               validates that a commit message matches the commitizen schema
    version             get the version of the installed commitizen or the current project (default: installed commitizen)
```

## Setting up bash completion

When using bash as your shell (limited support for zsh, fish, and tcsh is available), Commitizen can use [argcomplete](https://kislyuk.github.io/argcomplete/) for auto-completion. For this, argcomplete needs to be enabled.

argcomplete is installed when you install Commitizen since it's a dependency.

If Commitizen is installed globally, global activation can be executed:

```bash
sudo activate-global-python-argcomplete
```

For permanent (but not global) Commitizen activation, use:

```bash
register-python-argcomplete cz >> ~/.bashrc
```

For one-time activation of argcomplete for Commitizen only, use:

```bash
eval "$(register-python-argcomplete cz)"
```

For further information on activation, please visit the [argcomplete website](https://kislyuk.github.io/argcomplete/).

## Sponsors

These are our cool sponsors!

<!-- sponsors --><!-- sponsors -->

[conventional_commits]: https://www.conventionalcommits.org
[semver]: https://semver.org/
[keepchangelog]: https://keepachangelog.com/
[gitscm]: https://git-scm.com/downloads
