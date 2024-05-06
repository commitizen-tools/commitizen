## About

This command will generate a changelog following the committing rules established.

To create the changelog automatically on bump, add the setting [update_changelog_on_bump](./bump.md#update_changelog_on_bump)

```toml
[tool.commitizen]
update_changelog_on_bump = true
```

## Usage

![cz changelog --help](../images/cli_help/cz_changelog___help.svg)

### Examples

#### Generate full changelog

```bash
cz changelog
```

```bash
cz ch
```

#### Get the changelog for the given version

```bash
cz changelog 0.3.0 --dry-run
```

#### Get the changelog for the given version range

```bash
cz changelog 0.3.0..0.4.0 --dry-run
```

## Constrains

changelog generation is constrained only to **markdown** files.

## Description

These are the variables used by the changelog generator.

```md
# <version> (<date>)

## <change_type>

- **<scope>**: <message>
```

It will create a full block like above per version found in the tags.
And it will create a list of the commits found.
The `change_type` and the `scope` are optional, they don't need to be provided,
but if your regex does they will be rendered.

The format followed by the changelog is the one from [keep a changelog][keepachangelog]
and the following variables are expected:

| Variable      | Description                                                                                    | Source         |
| ------------- | ---------------------------------------------------------------------------------------------- | -------------- |
| `version`     | Version number which should follow [semver][semver]                                            | `tags`         |
| `date`        | Date in which the tag was created                                                              | `tags`         |
| `change_type` | The group where the commit belongs to, this is optional. Example: fix                          | `commit regex` |
| `message`\*   | Information extracted from the commit message                                                  | `commit regex` |
| `scope`       | Contextual information. Should be parsed using the regex from the message, it will be **bold** | `commit regex` |
| `breaking`    | Whether is a breaking change or not                                                            | `commit regex` |

- **required**: is the only one required to be parsed by the regex

## Configuration

### `unreleased_version`

There is usually a chicken and egg situation when automatically
bumping the version and creating the changelog.
If you bump the version first, you have no changelog, you have to
create it later, and it won't be included in
the release of the created version.

If you create the changelog before bumping the version, then you
usually don't have the latest tag, and the _Unreleased_ title appears.

By introducing `unreleased_version` you can prevent this situation.

Before bumping you can run:

```bash
cz changelog --unreleased-version="v1.0.0"
```

Remember to use the tag instead of the raw version number

For example if the format of your tag includes a `v` (`v1.0.0`), then you should use that,
if your tag is the same as the raw version, then ignore this.

Alternatively you can directly bump the version and create the changelog by doing

```bash
cz bump --changelog
```

### `file-name`

This value can be updated in the `toml` file with the key `changelog_file` under `tools.commitizen`

Specify the name of the output file, remember that changelog only works with markdown.

```bash
cz changelog --file-name="CHANGES.md"
```

### `incremental`

This flag can be set in the `toml` file with the key `changelog_incremental` under `tools.commitizen`

Benefits:

- Build from latest version found in changelog, this is useful if you have a different changelog and want to use commitizen
- Update unreleased area
- Allows users to manually touch the changelog without being rewritten.

```bash
cz changelog --incremental
```

```toml
[tools.commitizen]
# ...
changelog_incremental = true
```

### `start-rev`

This value can be set in the `toml` file with the key `changelog_start_rev` under `tools.commitizen`

Start from a given git rev to generate the changelog. Commits before that rev will not be considered. This is especially useful for long-running projects adopting conventional commits, where old commit messages might fail to be parsed for changelog generation.

```bash
cz changelog --start-rev="v0.2.0"
```

```toml
[tools.commitizen]
# ...
changelog_start_rev = "v0.2.0"
```

### merge-prerelease

This flag can be set in the `toml` file with the key `changelog_merge_prerelease` under `tools.commitizen`

Collects changes from prereleases into the next non-prerelease. This means that if you have a prerelease version, and then a normal release, the changelog will show the prerelease changes as part of the changes of the normal release. If not set, it will include prereleases in the changelog.

```bash
cz changelog --merge-prerelease
```

```toml
[tools.commitizen]
# ...
changelog_merge_prerelease = true
```

### `template`

Provides your own changelog jinja template by using the `template` settings or the `--template` parameter.
See [the template customization section](../customization.md#customizing-the-changelog-template)

### `extras`

Provides your own changelog extra variables by using the `extras` settings or the `--extra/-e` parameter.

```bash
cz changelog --extra key=value -e short="quoted value"
```

See [the template customization section](../customization.md#customizing-the-changelog-template)

## Hooks

Supported hook methods:

- per parsed message: useful to add links
- end of changelog generation: useful to send slack or chat message, or notify another department

Read more about hooks in the [customization page][customization]

[keepachangelog]: https://keepachangelog.com/
[semver]: https://semver.org/
[customization]: ../customization.md
