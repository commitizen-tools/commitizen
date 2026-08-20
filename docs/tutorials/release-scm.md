# Releasing with the SCM Version Provider

In this tutorial, you will learn how to bump the version using the `scp` version provider; as you can't use `cz bump`.

## About

When `version_provider` is set to `scm`, Commitizen reads the version directly from your Git tags instead of a config file.
This provider is **read-only**: it can determine the current version, but it cannot write a new one for you.

```toml title=".cz.toml"
[tool.commitizen]
tag_format = "v${version}"
version_provider = "scm"
```

This means `cz bump` cannot complete its usual job of writing the new version anywhere (see [Why can't I bump with SCM?](#why-cant-i-bump-with-scm) below). In the next section, you will learn how to do it anyways.

## Creating a New Version Tag Manually

To release a new version without an extra commit and using tags,
you can compute the next tag using `cz version` and then, you can manually create the tag directly.

In this example, we create an annotated tag with the changelog as the tag message, using just `git`.

```sh
next_version=$(cz version --project --next --tag)
cz changelog --incremental --dry-run --unreleased-version "$next_version" > .changelog.md
git tag --annotate "$next_version" -F .changelog.md
git push --follow-tags
```

!!! tip
    Wrap this in a CI job to fully automate releases when using the `scm` provider using [setup-cz](https://github.com/commitizen-tools/setup-cz)

## GitHub Action Example

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
          cz changelog --incremental --dry-run --unreleased-version "$next_version" > .changelog.md
          git tag --annotate "$next_version" -F .changelog.md
          git push --follow-tags
```

## Why Can't I Bump with SCM?

When you run `cz bump`, Commitizen normally creates a new commit that updates the version somewhere,
either in `.cz.toml`, or in `pyproject.toml` if you're using Python, or `Cargo.toml` for rust.
It may also update `version_files` and regenerate `CHANGELOG.md`.

Commitizen deliberately bundles a new release into a single "release commit".

This is core to its philosophy: the version should live in the code itself, not only in a Git tag,
so anyone can read the current version straight from the source, without needing to inspect the tags.

When a Git tag is the sole source of truth, that guarantee disappears,
the version becomes metadata layered on top of your history instead of something visible within the code itself.

Nonetheless, you can still do it.
