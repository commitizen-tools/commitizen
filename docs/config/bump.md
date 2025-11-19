# Bump Options

<!-- When adding a new option, please keep the alphabetical order. -->

## `annotated_tag`

When set to `true`, `cz bump` is equivalent to `cz bump --annotated-tag`.

```toml title="pyproject.toml"
[tool.commitizen]
annotated_tag = true
```

## `bump_message`

Template used to specify the commit message generated when bumping.

Defaults to: `bump: version $current_version → $new_version`

| Variable           | Description                         |
| ------------------ | ----------------------------------- |
| `$current_version` | the version existing before bumping |
| `$new_version`     | version generated after bumping     |

```toml title="pyproject.toml"
[tool.commitizen]
bump_message = "release $current_version → $new_version [skip-ci]"
```

## `gpg_sign`

When set to `true`, `cz bump` is equivalent to `cz bump --gpg-sign`. See [`--gpg-sign`](../commands/bump.md#-gpg-sign).

```toml title="pyproject.toml"
[tool.commitizen]
gpg_sign = true
```

## `ignored_tag_formats`

- Type: `list`
- Default: `[]`

Tags matching those formats will be totally ignored and won't raise a warning.
Each entry uses the syntax as [`tag_format`](#tag_format) with the addition of `*` that will match everything (non-greedy).

## `major_version_zero`

When set to `true`, `cz bump` is equivalent to `cz bump --major-version-zero`. See [`--major-version-zero`](../commands/bump.md#-major-version-zero).

```toml title="pyproject.toml"
[tool.commitizen]
major_version_zero = true
```

## `legacy_tag_formats`

- Type: `list`
- Default: `[]`

Legacy git tag formats, useful for old projects that changed tag format.
Tags matching those formats will be recognized as version tags and be included in the changelog.
Each entry uses the syntax as `tag_format`.

## `pre_bump_hooks`

A list of optional commands that will run right *after* updating [`version_files`](#version_files) and *before* actual committing and tagging the release.

Useful when you need to generate documentation based on the new version. During
execution of the script, some environment variables are available:

| Variable                     | Description                                                |
| ---------------------------- | ---------------------------------------------------------- |
| `CZ_PRE_IS_INITIAL`          | `True` when this is the initial release, `False` otherwise |
| `CZ_PRE_CURRENT_VERSION`     | Current version, before the bump                           |
| `CZ_PRE_CURRENT_TAG_VERSION` | Current version tag, before the bump                       |
| `CZ_PRE_NEW_VERSION`         | New version, after the bump                                |
| `CZ_PRE_NEW_TAG_VERSION`     | New version tag, after the bump                            |
| `CZ_PRE_MESSAGE`             | Commit message of the bump                                 |
| `CZ_PRE_INCREMENT`           | Whether this is a `MAJOR`, `MINOR` or `PATCH` release       |
| `CZ_PRE_CHANGELOG_FILE_NAME` | Path to the changelog file, if available                   |

```toml title="pyproject.toml"
[tool.commitizen]
pre_bump_hooks = [
  "scripts/generate_documentation.sh"
]
```

## `post_bump_hooks`

A list of optional commands that will run right *after* committing and tagging the release.

Useful when you need to send notifications about a release, or further automate deploying the
release. During execution of the script, some environment variables are available:

| Variable                       | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| `CZ_POST_WAS_INITIAL`          | `True` when this was the initial release, `False` otherwise |
| `CZ_POST_PREVIOUS_VERSION`     | Previous version, before the bump                           |
| `CZ_POST_PREVIOUS_TAG_VERSION` | Previous version tag, before the bump                       |
| `CZ_POST_CURRENT_VERSION`      | Current version, after the bump                             |
| `CZ_POST_CURRENT_TAG_VERSION`  | Current version tag, after the bump                         |
| `CZ_POST_MESSAGE`              | Commit message of the bump                                  |
| `CZ_POST_INCREMENT`            | Whether this was a `MAJOR`, `MINOR` or `PATCH` release      |
| `CZ_POST_CHANGELOG_FILE_NAME`  | Path to the changelog file, if available                    |

```toml title="pyproject.toml"
[tool.commitizen]
post_bump_hooks = [
  "scripts/slack_notification.sh"
]
```

## `prerelease_offset`

Offset with which to start counting prereleases.

If not specified, defaults to `0`.

```toml title="pyproject.toml"
[tool.commitizen]
prerelease_offset = 1
```

!!! note
    Under some circumstances, a prerelease cannot start with `0`-for example, in embedded projects where individual characters are encoded as bytes. You can specify an offset from which to start counting.

## `tag_format`

See [`--tag-format`](../commands/bump.md#-tag-format).

## `update_changelog_on_bump`

When set to `true`, `cz bump` is equivalent to `cz bump --changelog`.

```toml title="pyproject.toml"
[tool.commitizen]
update_changelog_on_bump = true
```

## `version_files`

Identify the files or glob patterns which should be updated with the new version.

Commitizen will update its configuration file automatically when bumping,
regardless of whether the file is present or not in `version_files`.

You may specify the `version_files` in your configuration file.

```toml title="pyproject.toml"
[tool.commitizen]
version_files = [
    "src/__version__.py",
]
```

It is also possible to provide a pattern for each file, separated by a colon (e.g. `file:pattern`). See the below example for more details.

```toml title="pyproject.toml"
[tool.commitizen]
version_files = [
    "packages/*/pyproject.toml:version",
    "setup.json:version",
]
```

!!! note "Example scenario"
    We have a project with the following configuration file `pyproject.toml`:

    ```toml title="pyproject.toml"
    [tool.commitizen]
    version_files = [
        "src/__version__.py",
        "packages/*/pyproject.toml:version",
        "setup.json:version",
    ]
    ```

    For the reference `"setup.json:version"`, it means that it will look for a file `setup.json` and will only change the lines that contain the substring `"version"`.

    For example, if the content of `setup.json` is:

    <!-- DEPENDENCY: repeated_version_number.json -->

    ```json title="setup.json"
    {
    "name": "magictool",
    "version": "1.2.3",
    "dependencies": {
        "lodash": "1.2.3"
    }
    }
    ```

    After running `cz bump 2.0.0`, its content will be updated to:

    ```diff title="setup.json"
    {
    "name": "magictool",
    - "version": "1.2.3",
    + "version": "2.0.0",
    "dependencies": {
        "lodash": "1.2.3"
    }
    }
    ```

!!! note
    Files can be specified using relative (to the execution) paths, absolute paths, or glob patterns.

!!! note "Historical note"
    This option was renamed from `files` to `version_files`.

## `version_scheme`

See [`--version-scheme`](../commands/bump.md#-version-scheme).
