This page contains frequently asked how to questions.

## Support for [`PEP621`](https://peps.python.org/pep-0621/)

`PEP621` establishes a `[project]` definition inside `pyproject.toml`

```toml
[project]
name = "spam"
version = "2.5.1"
```

Commitizen provides a [`PEP621` version provider](config/version_provider.md) to get and set version from this field.

You just need to set the proper `version_provider` setting:

```toml
[project]
name = "spam"
version = "2.5.1"

[tool.commitizen]
version_provider = "pep621"
```

## How to revert a bump?

If for any reason, the created tag and changelog were to be undone, this is the snippet:

```sh
git tag --delete <created_tag>
git reset HEAD~
git reset --hard HEAD
```

This will remove the last tag created, plus the commit containing the update to `.cz.toml` and the changelog generated for the version.

In case the commit was pushed to the server, you can remove it by running:

```sh
git push --delete origin <created_tag>
```

## How to handle revert commits?

```sh
git revert --no-commit <SHA>
git commit -m "revert: foo bar"
```

## I got `Exception [WinError 995] The I/O operation ...` error

This error was caused by a Python bug on Windows. It's been fixed by [cpython #22017](https://github.com/python/cpython/pull/22017), and according to Python's changelog, [3.8.6rc1](https://docs.python.org/3.8/whatsnew/changelog.html#python-3-8-6-release-candidate-1) and [3.9.0rc2](https://docs.python.org/3.9/whatsnew/changelog.html#python-3-9-0-release-candidate-2) should be the accurate versions first contain this fix. In conclusion, upgrade your Python version might solve this issue.

More discussion can be found in issue [#318](https://github.com/commitizen-tools/commitizen/issues/318).

## How to change the tag format ?

You can use the [`legacy_tag_formats`](config/bump.md#legacy_tag_formats) to list old tag formats.
New bumped tags will be in the new format but old ones will still work for:

- changelog generation (full, incremental and version range)
- bump new version computation (automatically guessed or increment given)


So given if you change from `myproject-$version` to `${version}` and then `v${version}`,
your Commitizen configuration will look like this:

```toml
tag_format = "v${version}"
legacy_tag_formats = [
    "${version}",
    "myproject-$version",
]
```

## How to avoid warnings for expected non-version tags?

You can explicitly ignore them with [`ignored_tag_formats`](config/bump.md#ignored_tag_formats).

```toml
tag_format = "v${version}"
ignored_tag_formats = [
    "stable",
    "component-*",
    "env/*",
    "v${major}.${minor}",
]
```
