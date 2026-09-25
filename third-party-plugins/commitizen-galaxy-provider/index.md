# [commitizen-galaxy-provider](https://github.com/shaps/commitizen-galaxy-provider)

A version provider to manage ansible collection versions. The provider updates the version in `galaxy.yml` so you can use commitizen to bump versions

## Installation

```
pip install commitizen-galaxy-provider
```

## Usage

Use `galaxy` as your `version_provider` in your config file

Example of `.cz.yaml`

```
---
commitizen:
  tag_format: $version
  version_provider: galaxy
  version_scheme: semver
```
