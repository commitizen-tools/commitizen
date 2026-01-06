# Configuration File

Commitizen uses configuration files to customize its behavior for your project. These files define settings such as which commit rules to use, version management preferences, changelog generation options, and more.

## Creating a Configuration File

It is recommended to create a configuration file via our [`cz init`](../commands/init.md) command. This command will guide you through setting up your configuration file with the appropriate settings for your project.

## File Location and Search Order

Configuration files are typically located in the root of your project directory. Commitizen searches for configuration files in the following order:

1. `pyproject.toml` (in the `[tool.commitizen]` section)
2. `.cz.toml`
3. `.cz.json`
4. `cz.json`
5. `.cz.yaml`
6. `cz.yaml`
7. `cz.toml`

The first valid configuration file found will be used. If no configuration file is found, Commitizen will use its default settings.

!!! note
    Commitizen supports explicitly specifying a configuration file using the `--config` option, which is useful when the configuration file is not located in the project root directory.
    When `--config` is provided, Commitizen will only load configuration from the specified file and will not search for configuration files using the default search order described above. If the specified configuration file does not exist, Commitizen raises the `ConfigFileNotFound` error. If the specified configuration file exists but is empty, Commitizen raises the `ConfigFileIsEmpty` error.

    ```bash
    cz --config <PATH> <command>
    ```

!!! tip
    For Python projects, it's recommended to add your Commitizen configuration to `pyproject.toml` to keep all project configuration in one place.

## Supported Formats

Commitizen supports three configuration file formats:

- **TOML** (`.toml`) - Recommended for Python projects
- **JSON** (`.json`)
- **YAML** (`.yaml`)

All formats support the same configuration options. Choose the format that best fits your project's ecosystem.

## Configuration Structure

### TOML Format

For TOML files, Commitizen settings are placed under the `[tool.commitizen]` section. If you're using a standalone `.cz.toml` or `cz.toml` file, you can use `[tool.commitizen]` or just `[commitizen]`.

**Example: `pyproject.toml`, `.cz.toml` or `cz.toml`**

```toml title="pyproject.toml"
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
version_provider = "commitizen"
version_scheme = "pep440"
version_files = [
    "src/__version__.py",
    "pyproject.toml:version"
]
tag_format = "$version"
update_changelog_on_bump = true
changelog_file = "CHANGELOG.md"
changelog_incremental = false
bump_message = "bump: version $current_version → $new_version"
gpg_sign = false
annotated_tag = false
major_version_zero = false
prerelease_offset = 0
retry_after_failure = false
allow_abort = false
message_length_limit = 0
allowed_prefixes = [
    "Merge",
    "Revert",
    "Pull request",
    "fixup!",
    "squash!",
    "amend!"
]
breaking_change_exclamation_in_title = false
use_shortcuts = false
pre_bump_hooks = []
post_bump_hooks = []
encoding = "utf-8"

# Optional: Custom styling for prompts
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

### JSON Format

For JSON files, Commitizen settings are placed under the `commitizen` key.

**Example: `.cz.json` or `cz.json`**

```json title=".cz.json"
{
  "commitizen": {
    "name": "cz_conventional_commits",
    "version": "0.1.0",
    "version_provider": "commitizen",
    "version_scheme": "pep440",
    "version_files": [
      "src/__version__.py",
      "pyproject.toml:version"
    ],
    "tag_format": "$version",
    "update_changelog_on_bump": true,
    "changelog_file": "CHANGELOG.md",
    "changelog_incremental": false,
    "bump_message": "bump: version $current_version → $new_version",
    "gpg_sign": false,
    "annotated_tag": false,
    "major_version_zero": false,
    "prerelease_offset": 0,
    "retry_after_failure": false,
    "allow_abort": false,
    "message_length_limit": 0,
    "allowed_prefixes": [
      "Merge",
      "Revert",
      "Pull request",
      "fixup!",
      "squash!",
      "amend!"
    ],
    "breaking_change_exclamation_in_title": false,
    "use_shortcuts": false,
    "pre_bump_hooks": [],
    "post_bump_hooks": [],
    "encoding": "utf-8",
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

### YAML Format

For YAML files, Commitizen settings are placed under the `commitizen` key.

**Example: `.cz.yaml` or `cz.yaml`**

```yaml title=".cz.yaml"
commitizen:
  name: cz_conventional_commits
  version: "0.1.0"
  version_provider: commitizen
  version_scheme: pep440
  version_files:
    - src/__version__.py
    - pyproject.toml:version
  tag_format: "$version"
  update_changelog_on_bump: true
  changelog_file: CHANGELOG.md
  changelog_incremental: false
  bump_message: "bump: version $current_version → $new_version"
  gpg_sign: false
  annotated_tag: false
  major_version_zero: false
  prerelease_offset: 0
  retry_after_failure: false
  allow_abort: false
  message_length_limit: 0
  allowed_prefixes:
    - Merge
    - Revert
    - Pull request
    - fixup!
    - squash!
    - amend!
  breaking_change_exclamation_in_title: false
  use_shortcuts: false
  pre_bump_hooks: []
  post_bump_hooks: []
  encoding: utf-8
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

## Configuration Options

For a complete list of all available configuration options and their descriptions, see the [Configuration Settings](../config/option.md) documentation.

Key configuration categories include:

- **Commit Rules**: `name` - Select which commit convention to use
- **Version Management**: `version`, `version_provider`, `version_scheme`, `version_files`
- **Tagging**: `tag_format`, `legacy_tag_formats`, `ignored_tag_formats`, `gpg_sign`, `annotated_tag`
- **Changelog**: `changelog_file`, `changelog_format`, `changelog_incremental`, `update_changelog_on_bump`
- **Bumping**: `bump_message`, `major_version_zero`, `prerelease_offset`, `pre_bump_hooks`, `post_bump_hooks`
- **Commit Validation**: `allowed_prefixes`, `message_length_limit`, `allow_abort`, `retry_after_failure`
- **Customization**: `customize`, `style`, `use_shortcuts`, `template`, `extras`

## Customization

For advanced customization, including creating custom commit rules, see the [Customization](../customization/config_file.md) documentation.

!!! note
    The `customize` option is only supported when using TOML configuration files.
