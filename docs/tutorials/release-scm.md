# Releasing with the SCM Version Provider

## About

When `version_provider` is set to `scm`, Commitizen reads the version directly from your Git tags instead of a config file.
This provider is **read-only**: it can determine the current version, but it cannot write a new one for you.

```toml title=".cz.toml"
[tool.commitizen]
tag_format = "v${version}"
version_provider = "scm"
```

This means `cz bump` cannot complete its usual job of writing the new version anywhere (see [Why can't I bump with SCM?](#why-cant-i-bump-with-scm) below).

## Creating a New Version Tag Manually

To release a new version without an extra commit, compute the next tag yourself and create it directly:

```sh
next_version=$(cz version --project --next --tag)
git tag --annotate "$next_version" --message "$next_version"
git push --follow-tags
```

!!! tip
    Wrap this in a CI job to fully automate releases when using the `scm` provider using [setup-cz](github.com/commitizen-tools/setup-cz)

## Why Can't I Bump with SCM?

When you run `cz bump`, Commitizen normally creates a new commit that updates the version somewhere,
either in `.cz.toml`, or in `pyproject.toml` if you're using Python, or `Cargo.toml` for rust.
It may also update `version_files` and regenerate `CHANGELOG.md`.

Commitizen deliberately bundles a new release into a single commit.
This is core to its philosophy: the version should live in the code itself, not only in a Git tag,
so anyone can read the current version straight from the source, without needing to inspect the tags.
When a Git tag is the sole source of truth, that guarantee disappears,
the version becomes metadata layered on top of your history instead of something visible within the code itself.

## Github action example

```yaml title=".github/workflows/bump-version.yml"
name: Bump version

on:
  push:
    branches:
      - main

jobs:
  bump:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: write
    steps:
      - uses: actions/checkout@v7
        with:
          token: "${{ secrets.PERSONAL_ACCESS_TOKEN }}"
          fetch-depth: 0
          fetch-tags: true
      - uses: commitizen-tools/setup-cz@main
        with:
          python-version: "3.x"
      - id: bump-version
        run: |
          next_version=$(cz version --project --next --tag)
          git tag --annotate "$next_version" --message "$next_version"
          git push --follow-tags
```
