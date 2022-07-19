# Configuration

## pyproject.toml or .cz.toml

Add an entry to `pyproject.toml` or `.cz.toml`. Recommended for **python** projects.

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

`.cz.toml` is recommended for **other languages** projects (js, go, etc).

## .cz.json or cz.json

JSON might be a more common configuration format for non-python projects, so Commitizen supports JSON config files, now.

```json
{
    "commitizen": {
        "name": "cz_conventional_commits",
        "version": "0.1.0",
        "version_files": [
            "src/__version__.py",
            "pyproject.toml:version"
        ],
        "style": [
            [
                "qmark",
                "fg:#ff9d00 bold"
            ],
            [
                "question",
                "bold"
            ],
            [
                "answer",
                "fg:#ff9d00 bold"
            ],
            [
                "pointer",
                "fg:#ff9d00 bold"
            ],
            [
                "highlighted",
                "fg:#ff9d00 bold"
            ],
            [
                "selected",
                "fg:#cc5454"
            ],
            [
                "separator",
                "fg:#cc5454"
            ],
            [
                "instruction",
                ""
            ],
            [
                "text",
                ""
            ],
            [
                "disabled",
                "fg:#858585 italic"
            ]
        ]
    }
}
```

## .cz.yaml or cz.yaml
YAML is another format for **non-python** projects as well, supported by Commitizen:

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
    - ''
  - - text
    - ''
  - - disabled
    - fg:#858585 italic
```

## Settings

| Variable                   | Type   | Default                     | Description                                                                                                                                                                                     |
| -------------------------- | ------ | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                     | `str`  | `"cz_conventional_commits"` | Name of the committing rules to use                                                                                                                                                             |
| `version`                  | `str`  | `None`                      | Current version. Example: "0.1.2"                                                                                                                                                               |
| `version_files`            | `list` | `[ ]`                       | Files were the version will be updated. A pattern to match a line, can also be specified, separated by `:` [See more][version_files]                                                            |
| `tag_format`               | `str`  | `None`                      | Format for the git tag, useful for old projects, that use a convention like `"v1.2.1"`. [See more][tag_format]                                                                                  |
| `tag_parser `              | `str`  | `.*`                        | Generate changelog using only tags matching the regex pattern (e.g. `"v([0-9.])*"`). [See more][tag_parser]                                                                                  |
| `update_changelog_on_bump` | `bool` | `false`                     | Create changelog when running `cz bump`                                                                                                                                                         |
| `annotated_tag`            | `bool` | `false`                     | Use annotated tags instead of lightweight tags. [See difference][annotated-tags-vs-lightweight]                                                                                                 |
| `bump_message`             | `str`  | `None`                      | Create custom commit message, useful to skip ci. [See more][bump_message]                                                                                                                       |
| `allow_abort`              | `bool` | `false`                     | Disallow empty commit messages, useful in ci. [See more][allow_abort]                                                                                                                           |
| `changelog_file`           | `str`  | `CHANGELOG.md`              | filename of exported changelog                                                                                                                                                                  |
| `changelog_incremental`    | `bool` | `false`                     | Update changelog with the missing versions. This is good if you don't want to replace previous versions in the file. Note: when doing `cz bump --changelog` this is automatically set to `true` |
| `changelog_start_rev`      | `str`  | `None`                      | Start from a given git rev to generate the changelog                                                                                                                                            |
| `style`                    | `list` | see above                   | Style for the prompts (It will merge this value with default style.) [See More (Styling your prompts with your favorite colors)][additional-features]                                           |
| `customize`                | `dict` | `None`                      | **This is only supported when config through `toml`.** Custom rules for committing and bumping. [See more][customization]                                                                       |
| `use_shortcuts`            | `bool` | `false`                     | If enabled, commitizen will show keyboard shortcuts when selecting from a list. Define a `key` for each of your choices to set the key. [See more][shortcuts]                                   |

[version_files]: bump.md#version_files
[tag_format]: bump.md#tag_format
[bump_message]: bump.md#bump_message
[tag_parser]: changelog.md#tag_parser
[allow_abort]: check.md#allow-abort
[additional-features]: https://github.com/tmbo/questionary#additional-features
[customization]: customization.md
[shortcuts]: customization.md#shortcut-keys
[annotated-tags-vs-lightweight]: https://stackoverflow.com/a/11514139/2047185
