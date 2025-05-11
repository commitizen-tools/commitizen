## Third-Party Commitizen Templates

In addition to the native templates, some alternative commit format templates
are available as PyPI packages (installable with `pip`).

### [Conventional JIRA](https://pypi.org/project/conventional-JIRA/)

Just like _conventional commit_ format, but the scope has been restricted to a
JIRA issue format, i.e. `project-issueNumber`. This standardises scopes in a
meaningful way.

#### Installation

```sh
pip install conventional-JIRA
```

### [GitHub JIRA Conventional](https://pypi.org/project/cz-github-jira-conventional/)

This plugin extends the commitizen tools by:

- requiring a JIRA issue id in the commit message
- creating links to GitHub commits in the CHANGELOG.md
- creating links to JIRA issues in the CHANGELOG.md

#### Installation

```sh
pip install cz-github-jira-conventional
```

For installation instructions (configuration and pre-commit) please visit [https://github.com/apheris/cz-github-jira-conventional](https://github.com/apheris/cz-github-jira-conventional)

### [cz-emoji](https://github.com/adam-grant-hendry/cz-emoji)

_conventional commit_ format, but with emojis

#### Installation

```sh
pip install cz-emoji
```

#### Usage

```sh
cz --name cz_emoji commit
```

### [cz-conventional-gitmoji](https://github.com/ljnsn/cz-conventional-gitmoji)

*conventional commit*s, but with [gitmojis](https://gitmoji.dev).

Includes a pre-commit hook that automatically adds the correct gitmoji to the commit message based on the conventional type.

#### Installation

```sh
pip install cz-conventional-gitmoji
```

#### Usage

```sh
cz --name cz_gitmoji commit
```

### [Commitizen emoji](https://pypi.org/project/commitizen-emoji/) (Unmaintained)

Just like _conventional commit_ format, but with emojis and optionally time spent and related tasks.

#### Installation

```sh
pip install commitizen-emoji
```

#### Usage

```sh
cz --name cz_commitizen_emoji commit
```

### [Conventional Legacy (cz_legacy)][1]

An extension of the _conventional commit_ format to include user-specified
legacy change types in the `CHANGELOG` while preventing the legacy change types
from being used in new commit messages

#### Installation

```sh
pip install cz_legacy
```

#### Usage

See the [README][1] for instructions on configuration

[1]: https://pypi.org/project/cz_legacy

## Third-Party Commitizen Providers

Commitizen can read and write version from different sources. In addition to the native providers, some alternative version sources are available as PyPI packages (installable with `pip`).

### [commitizen-deno-provider](https://pypi.org/project/commitizen-deno-provider/)

A provider for **Deno** projects. The provider updates the version in deno.json and jsr.json files.

#### Installation

```sh
pip install commitizen-deno-provider
```

#### Usage

Add `deno-provider` to your configuration file.

Example for `.cz.yaml`:

```yaml
---
commitizen:
  major_version_zero: true
  name: cz_conventional_commits
  tag_format: $version
  update_changelog_on_bump: true
  version_provider: deno-provider
  version_scheme: semver
```
