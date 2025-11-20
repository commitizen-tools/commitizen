# [commitizen-deno-provider](https://pypi.org/project/commitizen-deno-provider/)

A provider for **Deno** projects. The provider updates the version in `deno.json` and `jsr.json` files.

<!-- TODO: What features does the plugin provide? -->

## Installation

```sh
pip install commitizen-deno-provider
```

## Usage

Add `deno-provider` to your configuration file.

Example for `.cz.yaml`:

```yaml
---
commitizen:
  major_version_zero: true
  name: cz_conventional_commits
  tag_format: $version
  update_changelog_on_bump: true
  version_provider: deno-provider
  version_scheme: semver
```
