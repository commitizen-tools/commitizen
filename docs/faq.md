## Features we won't add

For a comprehensive list of features that have been considered but won't be implemented, please refer to our [issue tracker](https://github.com/commitizen-tools/commitizen/issues?q=is:issue%20state:closed%20label:%22issue-status:%20wont-fix%22%20OR%20label:%22issue-status:%20wont-implement%22).

- Enable multiple locations of config file `.cz.*` [#955](https://github.com/commitizen-tools/commitizen/issues/955)
- Create a flag to build the changelog from commits in multiple git repositories [#790](https://github.com/commitizen-tools/commitizen/issues/790)
- Global Configuration [#597](https://github.com/commitizen-tools/commitizen/issues/597)

## Support for PEP621

PEP621 establishes a `[project]` definition inside `pyproject.toml`

```toml
[project]
name = "spam"
version = "2.5.1"
```

Commitizen provides a [`pep621` version provider](config.md#version-providers) to get and set version from this field.
You just need to set the proper `version_provider` setting:

```toml
[project]
name = "spam"
version = "2.5.1"

[tool.commitizen]
version_provider = "pep621"
```

## Why are `revert` and `chore` valid types in the check pattern of cz conventional_commits but not types we can select?

`revert` and `chore` are added to the "pattern" in `cz check` in order to prevent backward errors, but officially they are not part of conventional commits, we are using the latest [types from Angular](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type) (they used to but were removed).
However, you can create a customized `cz` with those extra types. (See [Customization](customization.md)).

See more discussion in issue [#142](https://github.com/commitizen-tools/commitizen/issues/142) and [#36](https://github.com/commitizen-tools/commitizen/issues/36)

## How to revert a bump?

If for any reason, the created tag and changelog were to be undone, this is the snippet:

```sh
git tag --delete <created_tag>
git reset HEAD~
git reset --hard HEAD
```

This will remove the last tag created, plus the commit containing the update to `.cz.toml` and the changelog generated for the version.

In case the commit was pushed to the server you can remove it by running

```sh
git push --delete origin <created_tag>
```

## Is this project affiliated with the Commitizen JS project?

It is not affiliated.

Both are used for similar purposes, parsing commits, generating changelog and version we presume.
This one is written in python to make integration easier for python projects and the other serves the JS packages.

They differ a bit in design, not sure if cz-js does any of this, but these are some of the stuff you can do with this repo (python's commitizen):

- create custom rules, version bumps and changelog generation, by default we use the popular conventional commits (I think cz-js allows this).
- single package, install one thing and it will work (cz-js is a monorepo, but you have to install different dependencies AFAIK)
- pre-commit integration
- works on any language project, as long as you create the `.cz.toml` or `cz.toml` file.

Where do they cross paths?

If you are using conventional commits in your git history, then you could swap one with the other in theory.

Regarding the name, [cz-js][cz-js] came first, they used the word commitizen first. When this project was created originally, the creator read "be a good commitizen", and thought it was just a cool word that made sense, and this would be a package that helps you be a good "commit citizen".

[cz-js]: https://github.com/commitizen/cz-cli

## How to handle revert commits?

```sh
git revert --no-commit <SHA>
git commit -m "revert: foo bar"
```

## I got `Exception [WinError 995] The I/O operation ...` error

This error was caused by a Python bug on Windows. It's been fixed by [this PR](https://github.com/python/cpython/pull/22017), and according to Python's changelog, [3.8.6rc1](https://docs.python.org/3.8/whatsnew/changelog.html#python-3-8-6-release-candidate-1) and [3.9.0rc2](https://docs.python.org/3.9/whatsnew/changelog.html#python-3-9-0-release-candidate-2) should be the accurate versions first contain this fix. In conclusion, upgrade your Python version might solve this issue.

More discussion can be found in issue [#318](https://github.com/commitizen-tools/commitizen/issues/318).

## Why does commitizen not support CalVer?

`commitizen` could support CalVer alongside SemVer, but in practice implementing CalVer
creates numerous edge cases that are difficult to maintain ([#385]) and more generally
mixing the two version schemes may not be a good idea. If CalVer or other custom
versioning scheme is needed, `commitizen` could still be used to standardize commits
and create changelogs, but a separate package should be used for version increments.

Mixing CalVer and SemVer is generally not recommended because each versioning scheme
serves a different purposes. Diverging from either specification can be confusing to
users and cause errors with third party tools that don't expect the non-standard format.

In the future, `commitizen` may support some implementation of CalVer, but at the time
of writing, there are no plans to implement the feature ([#173]).

If you would like to learn more about both schemes, there are plenty of good resources:

- [Announcing CalVer](https://sedimental.org/calver.html)
- [API Versioning from Stripe](https://stripe.com/blog/api-versioning)
- [Discussion about pip's use of CalVer](https://github.com/pypa/pip/issues/5645#issuecomment-407192448)
- [Git Version Numbering](https://code.erpenbeck.io/git/2021/12/16/git-version-numbering/)
- [SemVer vs. CalVer and Why I Use Both](https://mikestaszel.com/2021/04/03/semver-vs-calver-and-why-i-use-both/) (but not at the same time)
- [Semver Will Not Save You](https://hynek.me/articles/semver-will-not-save-you/)
- [Why I Don't Like SemVer](https://snarky.ca/why-i-dont-like-semver/)

[#173]: https://github.com/commitizen-tools/commitizen/issues/173
[#385]: https://github.com/commitizen-tools/commitizen/pull/385

## How to change the tag format ?

You can use the [`legacy_tag_formats`](config.md#legacy_tag_formats) to list old tag formats.
New bumped tags will be in the new format but old ones will still work for:
- changelog generation (full, incremental and version range)
- bump new version computation (automatically guessed or increment given)


So given if you change from `myproject-$version` to `${version}` and then `v${version}`,
your commitizen configuration will look like this:

```toml
tag_format = "v${version}"
legacy_tag_formats = [
    "${version}",
    "myproject-$version",
]
```

## How to avoid warnings for expected non-version tags

You can explicitly ignore them with [`ignored_tag_formats`](config.md#ignored_tag_formats).

```toml
tag_format = "v${version}"
ignored_tag_formats = [
    "stable",
    "component-*",
    "env/*",
    "v${major}.${minor}",
]
```
