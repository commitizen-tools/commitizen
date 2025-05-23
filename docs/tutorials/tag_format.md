# Managing tag formats

## Tag format and version scheme

For most projects, the tag format is simply the version number which is set like this:

```yaml
[tool.commitizen]
tag_format: $version
version_scheme: pep440
```

As this is the default value, you don't have to specify it.

This setting means that:

- The tag generated on bump will have this format: `1.0.0` :
    - the version is generated following PEP440 scheme
    - the tag is exactly the generated version
- All tags having this format will be recognized as version tag when:
    - searching the last while bumping a release
    - searching previous versions while:
        - generating incremental changelog
        - generating a changelog for a version range
- The changelog versions (section titles) will have this format
- The `scm` version provider will identify the current version using this tag format

The version format will change depending on your configured version scheme.
For most, it will only impact pre-releases and [developmental releases](dev_releases.md) formats (i.e. `1.0.0-rc.1` vs. `1.0.0.rc1`)

But you may need a different tagging convention, let's say using `semver` and prefixed with a `v`.
In this case you will define your settings like this:

```yaml
[tool.commitizen]
tag_format: v${version}
version_scheme: semver
```

As a result, the tag generated on bump will have this format: `v1.0.0` and the version will be generated following `semver` scheme.

!!! note
    Both `$version` and `${version}` syntaxes are strictly equivalent. You can use the one you prefer.

See [the `version_scheme` section in `bump` command documentation](../commands/bump.md#version_scheme) for more details on version schemes and how to define your own.
See [`tag_format`](../config.md#tag_format) and [`version_scheme`](../config.md#version_scheme) settings in [Configuration reference](../config.md) for more details on these settings.

## Changing convention

Now, let's say you need to change the tag format for some reason (company convention, [migration to a monorepo](monorepo_guidance.md)...).
You will obviously want to keep all those features working as expected.

Commitizen can deal with it as long as you provide the legacy tag format in the configuration.

Using the previous example, let's say you want to move from `v${version}` to `component-${version}`.
Then `component-${version}` will be the new tag format and `v${version}` the legacy one.

```yaml
[tool.commitizen]
tag_format: component-${version}
legacy_tag_formats:
 - v${version}
```

This way, you won't lose your version history, you'll still be able to generate your changelog properly,
and on the next version bump, your last version in the form `v${version}` will be properly recognized if you use the `scm` version provider.
Your new tag will be in the form `component-${version}`.

## Known tags to ignore

Now let's say you have some known tags you want to ignore, either because they are not versions, or because they are not versions of the component you are dealing with.
As a consequence, you don't want them to trigger a warning because Commitizen detected an unknown tag format.

Then you can tell Commitizen about it using the [`ignored_tag_formats`](../config.md#ignored_tag_formats) setting:

```yaml
[tool.commitizen]
ignored_tag_formats:
  - prod
  - other-component-${version}
  - prefix-*
```

This will ignore:

- The `prod` tag
- Any version tag prefixed with `other-component-`
- Any tag prefixed with `prefix-`


!!! tip
    Note the `*` in the `prefix-*` pattern. This is a wildcard and only exists for `ignored_tag_formats`.
    It will match any string from any length. This allows to exclude by prefix, whether it is followed by a version or not.

!!! tip
    If you don't want to be warned when Commitizen detects an unknown tag, you can do so by setting:
    ```
    [tool.commitizen]
    ignored_tag_formats = ["*"]
    ```
    But be aware that you will not be warned if you have a typo in your tag formats.
