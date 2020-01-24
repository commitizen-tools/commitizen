# Configuration

Commitizen has support for `toml` and `ini` files. It first looks up the configuration file in the current working directory and then the root directory of the git project.

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

## INI files

**INI files will not be supported in the next major version. Please use toml instead**

Supported files: `.cz`, `.cz.cfg`, `setup.cfg`, and `$HOME/.cz`

The format is slightly different to the `toml`, so pay attention.
Recommended for **other languages** projects (js, go, etc).

```ini
[commitizen]
name = cz_conventional_commits
version = 0.1.0
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

The extra tab before the square brackets (`]`) at the end is required.

## Settings

| Variable | Type | Default | Description |
| -------- | ---- | ------- | ----------- |
| `name` | `str` | `"cz_conventional_commits"` | Name of the committing rules to use |
| `version` | `str` | `None` | Current version. Example: "0.1.2" |
| `version_files` | `list` | `[ ]` | Files were the version will be updated. A pattern to match a line, can also be specified, separated by `:` [See more](https://woile.github.io/commitizen/bump#files) |
| `tag_format` | `str` | `None` | Format for the git tag, useful for old projects, that use a convention like `"v1.2.1"`. [See more](https://woile.github.io/commitizen/bump#tag_format) |
| `bump_message` | `str` | `None` | Create custom commit message, useful to skip ci. [See more](https://woile.github.io/commitizen/bump#bump_message) |
| `changelog_file` | `str` | `CHANGELOG.md` | filename of exported changelog |
| `style` | `list` | see above | Style for the prompts (It will merge this value with default style.) [See More (Styling your prompts with your favorite colors)](https://github.com/tmbo/questionary#additional-features) |
| `customize` | `dict` | `None` | **This is only supported when config through `toml`.** Custom rules for committing and bumping. [See more](https://commitizen-tools.github.io/commitizen/customization/) |
