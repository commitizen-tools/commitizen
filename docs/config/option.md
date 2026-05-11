# General Options

## `name`

Name of the committing rules to use. What we generally call the **commit conventions**.

- Type: `str`
- Default: `"cz_conventional_commits"`
- Options
    - `cz_conventional_commits`: uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
    - `cz_jira`: jira [smart commits](https://support.atlassian.com/bitbucket-cloud/docs/use-smart-commits/)
    - `cz_customize`: (**not recommended**) customize the convention directly in the `TOML` file under `[tool.commitizen.customize]`, read [Customize in configuration file](../customization/config_file.md) for more. There's a plan to provide a different functionality.

You can write your own convention, and release it on PyPI, check [Customizing through a Python class](../customization/python_class.md).

## `version`

Current version.

Required if you use `version_provider = "commitizen"`.

- Type: `str`
- Default: `None`

Example: `"0.1.2"`.

## `style`

Style for the prompts.

- Type: `list`
- Default: `[]`

It will merge this value with default style. See [Styling your prompts with your favorite colors](https://github.com/tmbo/questionary#additional-features) for more details.

## `customize`

Custom rules for committing and bumping.

- Type: `dict`
- Default: `None`

**Supported in TOML, JSON, and YAML configuration files.**

See [customization](../customization/config_file.md) for more details.

## `strict_config`

When enabled, Commitizen raises an error if the configuration file contains
keys that are not recognized as valid commitizen settings (for example because
of a typo such as `update_changelog_on_bumb` instead of
`update_changelog_on_bump`).

When disabled (the default), unknown keys only produce a warning so they can be
spotted without breaking existing setups.

- Type: `bool`
- Default: `False`

**Example**

```toml title="pyproject.toml"
[tool.commitizen]
name = "cz_conventional_commits"
strict_config = true
```

If you intentionally need to keep additional plugin-specific data inside the
commitizen section, put it under the `extras` setting so it is not flagged as
unknown.

## `use_shortcuts`

Show keyboard shortcuts when selecting from a list. When enabled, each choice shows a shortcut key; press that key or use the arrow keys to select.

- Type: `bool`
- Default: `False`

**Example**

```toml title="pyproject.toml"
[tool.commitizen]
name = "cz_conventional_commits"
use_shortcuts = true
```

Run `cz commit` to see shortcut keys on each choice.

![Menu with shortcut keys](../images/cli_interactive/shortcut_default.gif)

To customize which key is used for each choice (via the `key` field when using `cz_customize`), see [shortcut keys customization](../customization/config_file.md#shortcut-keys).
