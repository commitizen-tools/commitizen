# Configuration

## Settings

| Variable                   | Type   | Default                     | Description                                                                                                                                                                                                                                          |
| -------------------------- | ------ | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                     | `str`  | `"cz_conventional_commits"` | Name of the committing rules to use                                                                                                                                                                                                                  |
| `version`                  | `str`  | `None`                      | Current version. Example: "0.1.2"                                                                                                                                                                                                                    |
| `version_files`            | `list` | `[ ]`                       | Files were the version will be updated. A pattern to match a line, can also be specified, separated by `:` [See more][version_files]                                                                                                                 |
| `tag_format`               | `str`  | `None`                      | Format for the git tag, useful for old projects, that use a convention like `"v1.2.1"`. [See more][tag_format]                                                                                                                                       |
| `update_changelog_on_bump` | `bool` | `false`                     | Create changelog when running `cz bump`                                                                                                                                                                                                              |
| `gpg_sign`                 | `bool` | `false`                     | Use gpg signed tags instead of lightweight tags.                                                                                                                                                                                                     |
| `annotated_tag`            | `bool` | `false`                     | Use annotated tags instead of lightweight tags. [See difference][annotated-tags-vs-lightweight]                                                                                                                                                      |
| `bump_message`             | `str`  | `None`                      | Create custom commit message, useful to skip ci. [See more][bump_message]                                                                                                                                                                            |
| `allow_abort`              | `bool` | `false`                     | Disallow empty commit messages, useful in ci. [See more][allow_abort]                                                                                                                                                                                |
| `changelog_file`           | `str`  | `CHANGELOG.md`              | filename of exported changelog                                                                                                                                                                                                                       |
| `changelog_incremental`    | `bool` | `false`                     | Update changelog with the missing versions. This is good if you don't want to replace previous versions in the file. Note: when doing `cz bump --changelog` this is automatically set to `true`                                                      |
| `changelog_start_rev`      | `str`  | `None`                      | Start from a given git rev to generate the changelog                                                                                                                                                                                                 |
| `style`                    | `list` | see above                   | Style for the prompts (It will merge this value with default style.) [See More (Styling your prompts with your favorite colors)][additional-features]                                                                                                |
| `customize`                | `dict` | `None`                      | **This is only supported when config through `toml`.** Custom rules for committing and bumping. [See more][customization]                                                                                                                            |
| `use_shortcuts`            | `bool` | `false`                     | If enabled, commitizen will show keyboard shortcuts when selecting from a list. Define a `key` for each of your choices to set the key. [See more][shortcuts]                                                                                        |
| `major_version_zero`       | `bool` | `false`                     | When true, breaking changes on a `0.x` will remain as a `0.x` version. On `false`, a breaking change will bump a `0.x` version to `1.0`. [major-version-zero]                                                                                        |
| `prerelease_offset`        | `int`  | `0`                         | In special cases it may be necessary that a prerelease cannot start with a 0, e.g. in an embedded project the individual characters are encoded in bytes. This can be done by specifying an offset from which to start counting. [prerelease-offset] |

## pyproject.toml or .cz.toml

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

## .cz.json or cz.json

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

## .cz.yaml or cz.yaml

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

[version_files]: bump.md#version_files
[tag_format]: bump.md#tag_format
[bump_message]: bump.md#bump_message
[major-version-zero]: bump.md#-major-version-zero
[prerelease-offset]: bump.md#-prerelease_offset
[allow_abort]: check.md#allow-abort
[additional-features]: https://github.com/tmbo/questionary#additional-features
[customization]: customization.md
[shortcuts]: customization.md#shortcut-keys
[annotated-tags-vs-lightweight]: https://stackoverflow.com/a/11514139/2047185
