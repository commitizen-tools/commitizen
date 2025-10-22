## Third-Party Commitizen Templates

In addition to the native templates, some alternative commit format templates
are available as PyPI packages (installable with `pip`).

### [cz-ai](https://github.com/watadarkstar/cz_ai)

A Commitizen plugin that leverages OpenAI's GPT-4o to automatically generate clear, concise, and conventional commit messages based on your staged git changes.

#### Installation

```sh
pip install cz-ai
```

#### Usage

```sh
cz --name cz_ai commit
```

### [Conventional JIRA](https://pypi.org/project/conventional-JIRA/)

Just like _conventional commit_ format, but the scope has been restricted to a
JIRA issue format, i.e. `project-issueNumber`. This standardises scopes in a
meaningful way.

#### Installation

```sh
pip install conventional-JIRA
```

### [GitHub JIRA Conventional](https://pypi.org/project/cz-github-jira-conventional/)

This plugin extends the Commitizen tools by:

- requiring a JIRA issue ID in the commit message
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

### [cz-path](https://pypi.org/project/cz-path/)

Provides prefix choices for commit messages based on staged files (Git only).
For example, if the staged files are `component/z/a.ts` and `component/z/b.ts`,
the path prefix option will be `component/z` and commit message might look like:
`component/z/: description of changes`. If only one file is staged, the extension
is removed in the prefix.

#### Installation

```sh
pip install cz-path
```

#### Usage

Add `cz-path` to your configuration file.

Example for `.cz.json`:

```json
{
  "commitizen": {
    "name": "cz_path",
    "remove_path_prefixes": ["src", "module_name"]
  }
}
```

The default value for `remove_path_prefixes` is `["src"]`. Adding `/` to the
prefixes is not required.

#### Example session

```plain
 $ git add .vscode/
 $ cz -n cz_path c
? Prefix: (Use arrow keys)
 » .vscode
   .vscode/
   project
   (empty)
? Prefix: .vscode
? Commit title: adjust settings

.vscode: adjust settings

[main 0000000] .vscode: adjust settings
 2 files changed, 1 insertion(+), 11 deletions(-)

Commit successful!
```
