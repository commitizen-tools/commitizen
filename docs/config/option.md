# Misc Options

## `name`

- Type: `str`
- Default: `"cz_conventional_commits"`

Name of the committing rules to use.

## `version`

- Type: `str`
- Default: `None`

Current version. Example: `"0.1.2"`. Required if you use `version_provider = "commitizen"`.

## `style`

- Type: `list`
- Default: `[]`

Style for the prompts (It will merge this value with default style.) See [Styling your prompts with your favorite colors](https://github.com/tmbo/questionary#additional-features) for more details.

## `customize`

- Type: `dict`
- Default: `None`

**This is only supported when config through `toml` configuration file.**

Custom rules for committing and bumping. See [customization](../customization/config_file.md) for more details.

## `use_shortcuts`

- Type: `bool`
- Default: `False`

Show keyboard shortcuts when selecting from a list. Define a `key` for each of your choices to set the key. See [shortcut keys](../customization/config_file.md#shortcut-keys) for more details.
