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

**Supported in TOML, JSON, and YAML configuration files.**

Custom rules for committing and bumping. See [customization](../customization/config_file.md) for more details.

## `use_shortcuts`

- Type: `bool`
- Default: `False`

Show keyboard shortcuts when selecting from a list. When enabled, each choice shows a shortcut key; press that key or use the arrow keys to select.

Example:

```toml title="pyproject.toml"
[tool.commitizen]
name = "cz_conventional_commits"
use_shortcuts = true
```

Run `cz commit` to see shortcut keys on each choice.

![Menu with shortcut keys](../images/cli_interactive/shortcut_default.gif)

To customize which key is used for each choice (via the `key` field when using `cz_customize`), see [shortcut keys customization](../customization/config_file.md#shortcut-keys).
