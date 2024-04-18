# Configuration

## Settings

### `name`

Type: `str`

Default: `"cz_conventional_commits"`

Name of the committing rules to use

### `version`

Type: `str`

Default: `None`

Current version. Example: "0.1.2". Required if you use `version_provider = "commitizen"`.

### `version_files`

Type: `list`

Default: `[ ]`

Files were the version will be updated. A pattern to match a line, can also be specified, separated by `:` [Read more][version_files]

### `version_provider`

Type: `str`

Default: `commitizen`

Version provider used to read and write version [Read more](#version-providers)

### `version_scheme`

Type: `str`

Default: `pep440`

Select a version scheme from the following options [`pep440`, `semver`, `semver2`].
Useful for non-python projects. [Read more][version-scheme]

### `tag_format`

Type: `str`

Default: `$version`

Format for the git tag, useful for old projects, that use a convention like `"v1.2.1"`. [Read more][tag_format]

### `update_changelog_on_bump`

Type: `bool`

Default: `false`

Create changelog when running `cz bump`

### `gpg_sign`

Type: `bool`

Default: `false`

Use gpg signed tags instead of lightweight tags.

### `annotated_tag`

Type: `bool`

Default: `false`

Use annotated tags instead of lightweight tags. [See difference][annotated-tags-vs-lightweight]

### `bump_message`

Type: `str`

Default: `None`

Create custom commit message, useful to skip ci. [Read more][bump_message]

### `retry_after_failure`

Type: `bool`

Default: `false`

Automatically retry failed commit when running `cz commit`. [Read more][retry_after_failure]

### `allow_abort`

Type: `bool`

Default: `false`

Disallow empty commit messages, useful in ci. [Read more][allow_abort]

### `allowed_prefixes`

Type: `list`
Default: `[ "Merge", "Revert", "Pull request", "fixup!", "squash!"]`
Allow some prefixes and do not try to match the regex when checking the message [Read more][allowed_prefixes]

### `changelog_file`

Type: `str`

Default: `CHANGELOG.md`

Filename of exported changelog

### `changelog_format`

Type: `str`

Default: None

Format used to parse and generate the changelog, If not specified, guessed from [`changelog_file`](#changelog_file).

### `changelog_incremental`

Type: `bool`

Default: `false`

Update changelog with the missing versions. This is good if you don't want to replace previous versions in the file. Note: when doing `cz bump --changelog` this is automatically set to `true`

### `changelog_start_rev`

Type: `str`

Default: `None`

Start from a given git rev to generate the changelog

### `changelog_merge_prerelease`

Type: `bool`

Default: `false`

Collect all changes of prerelease versions into the next non-prerelease version when creating the changelog.

### `style`

Type: `list`

see above

Style for the prompts (It will merge this value with default style.) [See More (Styling your prompts with your favorite colors)][additional-features]

### `customize`

Type: `dict`

Default: `None`

**This is only supported when config through `toml`.** Custom rules for committing and bumping. [Read more][customization]

### `use_shortcuts`

Type: `bool`

Default: `false`

If enabled, commitizen will show keyboard shortcuts when selecting from a list. Define a `key` for each of your choices to set the key. [Read more][shortcuts]

### `major_version_zero`

Type: `bool`

Default: `false`

When true, breaking changes on a `0.x` will remain as a `0.x` version. On `false`, a breaking change will bump a `0.x` version to `1.0`. [major-version-zero]

### `prerelease_offset`

Type: `int`

Default: `0`

In some circumstances, a prerelease cannot start with a 0, e.g. in an embedded project individual characters are encoded as bytes. This can be done by specifying an offset from which to start counting. [prerelease-offset]

### `pre_bump_hooks`

Type: `list[str]`

Default: `[]`

Calls the hook scripts **before** bumping version. [Read more][pre_bump_hooks]

### `post_bump_hooks`

Type: `list[str]`

Default: `[]`

Calls the hook scripts **after** bumping the version. [Read more][post_bump_hooks]

### `encoding`

Type: `str`

Default: `utf-8`

Sets the character encoding to be used when parsing commit messages. [Read more][encoding]

### `template`

Type: `str`

Default: `None` (provided by plugin)

Provide custom changelog jinja template path relative to the current working directory. [Read more][template-customization]

### `extras`

Type: `dict[str, Any]`

Default: `{}`

Provide extra variables to the changelog template. [Read more][template-customization]

## Configuration file

### pyproject.toml or .cz.toml

Default and recommended configuration format for a project.
For a **python** project, we recommend adding an entry to your `pyproject.toml`.
You can also create a `.cz.toml` file at the root of your project folder.

Example configuration:

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
version_files = [
    "src/__version__.py",
    "pyproject.toml:version"
]
update_changelog_on_bump = true
style = [
    ["qmark", "fg:#ff9d00 bold"],
    ["question", "bold"],
    ["answer", "fg:#ff9d00 bold"],
    ["pointer", "fg:#ff9d00 bold"],
    ["highlighted", "fg:#ff9d00 bold"],
    ["selected", "fg:#cc5454"],
    ["separator", "fg:#cc5454"],
    ["instruction", ""],
    ["text", ""],
    ["disabled", "fg:#858585 italic"]
]
```

### .cz.json or cz.json

Commitizen has support for JSON configuration. Recommended for `NodeJS` projects.

```json
{
  "commitizen": {
    "name": "cz_conventional_commits",
    "version": "0.1.0",
    "version_files": ["src/__version__.py", "pyproject.toml:version"],
    "style": [
      ["qmark", "fg:#ff9d00 bold"],
      ["question", "bold"],
      ["answer", "fg:#ff9d00 bold"],
      ["pointer", "fg:#ff9d00 bold"],
      ["highlighted", "fg:#ff9d00 bold"],
      ["selected", "fg:#cc5454"],
      ["separator", "fg:#cc5454"],
      ["instruction", ""],
      ["text", ""],
      ["disabled", "fg:#858585 italic"]
    ]
  }
}
```

### .cz.yaml or cz.yaml

YAML configuration is supported by Commitizen. Recommended for `Go`, `ansible`, or even `helm` charts projects.

```yaml
commitizen:
  name: cz_conventional_commits
  version: 0.1.0
  version_files:
    - src/__version__.py
    - pyproject.toml:version
  style:
    - - qmark
      - fg:#ff9d00 bold
    - - question
      - bold
    - - answer
      - fg:#ff9d00 bold
    - - pointer
      - fg:#ff9d00 bold
    - - highlighted
      - fg:#ff9d00 bold
    - - selected
      - fg:#cc5454
    - - separator
      - fg:#cc5454
    - - instruction
      - ""
    - - text
      - ""
    - - disabled
      - fg:#858585 italic
```

## Version providers

Commitizen can read and write version from different sources.
By default, it use the `commitizen` one which is using the `version` field from the commitizen settings.
But you can use any `commitizen.provider` entrypoint as value for `version_provider`.

Commitizen provides some version providers for some well known formats:

| name         | description                                                                                                                                                                                                             |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commitizen` | Default version provider: Fetch and set version in commitizen config.                                                                                                                                                   |
| `scm`        | Fetch the version from git and does not need to set it back                                                                                                                                                             |
| `pep621`     | Get and set version from `pyproject.toml` `project.version` field                                                                                                                                                       |
| `poetry`     | Get and set version from `pyproject.toml` `tool.poetry.version` field                                                                                                                                                   |
| `cargo`      | Get and set version from `Cargo.toml` `project.version` field                                                                                                                                                           |
| `npm`        | Get and set version from `package.json` `version` field, `package-lock.json` `version,packages.''.version` fields if the file exists, and `npm-shrinkwrap.json` `version,packages.''.version` fields if the file exists |
| `composer`   | Get and set version from `composer.json` `project.version` field                                                                                                                                                        |

!!! note
The `scm` provider is meant to be used with `setuptools-scm` or any packager `*-scm` plugin.

An example in your `.cz.toml` would look like this:

```toml
[tool.commitizen]
version_provider = "pep621"
```

### Custom version provider

You can add you own version provider by extending `VersionProvider` and exposing it on the `commitizen.provider` entrypoint.

Here a quick example of a `my-provider` provider reading and writing version in a `VERSION` file.

```python title="my_provider.py"
from pathlib import Path
from commitizen.providers import VersionProvider


class MyProvider(VersionProvider):
    file = Path() / "VERSION"

    def get_version(self) -> str:
        return self.file.read_text()

    def set_version(self, version: str):
        self.file.write_text(version)

```

```python title="setup.py"
from setuptools import setup

setup(
    name='my-commitizen-provider',
    version='0.1.0',
    py_modules=['my_provider'],
    install_requires=['commitizen'],
    entry_points = {
        'commitizen.provider': [
            'my-provider = my_provider:MyProvider',
        ]
    }
)
```

[version_files]: bump.md#version_files
[tag_format]: bump.md#tag_format
[bump_message]: bump.md#bump_message
[major-version-zero]: bump.md#-major-version-zero
[prerelease-offset]: bump.md#-prerelease_offset
[retry_after_failure]: commit.md#retry
[allow_abort]: check.md#allow-abort
[version-scheme]: bump.md#version-scheme
[pre_bump_hooks]: bump.md#pre_bump_hooks
[post_bump_hooks]: bump.md#post_bump_hooks
[allowed_prefixes]: check.md#allowed-prefixes
[additional-features]: https://github.com/tmbo/questionary#additional-features
[customization]: customization.md
[shortcuts]: customization.md#shortcut-keys
[template-customization]: customization.md#customizing-the-changelog-template
[annotated-tags-vs-lightweight]: https://stackoverflow.com/a/11514139/2047185
[encoding]: tutorials/writing_commits.md#writing-commits
