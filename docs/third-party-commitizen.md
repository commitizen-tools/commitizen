## Third-Party Commitizen Templates

In addition to the native templates, some alternative commit format templates
are available as PyPI packages (installable with `pip`).

### [Conventional JIRA](https://pypi.org/project/conventional-JIRA/)

Just like *conventional commit* format, but the scope has been restricted to a
JIRA issue format, i.e. `project-issueNumber`. This standardises scopes in a
meaningful way.

### Installation

```sh
pip install conventional-JIRA
```

### [GitHub JIRA Conventional](https://pypi.org/project/cz-github-jira-conventional/)

This plugin extends the commitizen tools by:
- requiring a JIRA issue id in the commit message
- creating links to GitHub commits in the CHANGELOG.md
- creating links to JIRA issues in the CHANGELOG.md

### Installation

```sh
pip install cz-github-jira-conventional
```

For installation instructions (configuration and pre-commit) please visit https://github.com/apheris/cz-github-jira-conventional

### [cz-emoji](https://github.com/adam-grant-hendry/cz-emoji)

*conventional commit* format, but with emojis

### Installation

```sh
pip install cz-emoji
```

### Usage

```sh
cz --name cz_emoji commit
```

### [cz-conventional-gitmoji](https://github.com/ljnsn/cz-conventional-gitmoji)

*conventional commit*s, but with [gitmojis](https://gitmoji.dev).

Includes a pre-commit hook that automatically adds the correct gitmoji to the commit message based on the conventional type.

### Installation

```bash
pip install cz-conventional-gitmoji
```

### Usage

```bash
cz --name cz_gitmoji commit
```


### [Commitizen emoji](https://pypi.org/project/commitizen-emoji/) (Unmaintained)

Just like *conventional commit* format, but with emojis and optionally time spent and related tasks.

It can be installed with `pip install commitizen-emoji`.

Usage: `cz --name cz_commitizen_emoji commit`.

### [Conventional Legacy (cz_legacy)][1]

An extension of the *conventional commit* format to include user-specified
legacy change types in the `CHANGELOG` while preventing the legacy change types
from being used in new commit messages

`cz_legacy` can be installed with `pip install cz_legacy`

See the [README][1] for instructions on configuration

  [1]: https://pypi.org/project/cz_legacy
