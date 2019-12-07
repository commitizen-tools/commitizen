![Bump version](images/bump.gif)

## About

The version is bumped **automatically** based on the commits.

The commits should follow the rules of the commiter in order to be parsed properly.

It is possible to specify a **prerelease** (alpha, beta, release candidate) version.

The version can also be **manually** bumped.

The version format follows [semantic versioning][semver].

This means `MAJOR.MINOR.PATCH`

| Increment | Description                 | Conventional commit map |
| --------- | --------------------------- | ----------------------- |
| `MAJOR`   | Breaking changes introduced | `BREAKING CHANGE`       |
| `MINOR`   | New features                | `feat`                  |
| `PATCH`   | Fixes                       | `fix` + everything else |

Prereleases are supported following python's [PEP 0440][pep440]

The scheme of this format is

```bash
[N!]N(.N)*[{a|b|rc}N][.postN][.devN]
```

Some examples:

```bash
0.9.0
0.9.1
0.9.2
0.9.10
0.9.11
1.0.0a0  # alpha
1.0.0a1
1.0.0b0  # beta
1.0.0rc0 # release candidate
1.0.0rc1
1.0.0
1.0.1
1.1.0
2.0.0
2.0.1a
```

`post` and `dev` releases are not supported yet.

## Usage

```bash
$ cz bump --help
usage: cz bump [-h] [--dry-run] [--files-only] [--yes]
               [--tag-format TAG_FORMAT] [--bump-message BUMP_MESSAGE]
               [--prerelease {alpha,beta,rc}]
               [--increment {MAJOR,MINOR,PATCH}]

optional arguments:
  -h, --help            show this help message and exit
  --dry-run             show output to stdout, no commit, no modified files
  --files-only          bump version in the files from the config
  --yes                 accept automatically questions done
  --tag-format TAG_FORMAT
                        format used to tag the commmit and read it, use it in
                        existing projects, wrap around simple quotes
  --bump-message BUMP_MESSAGE
                        template used to create the release commmit, useful
                        when working with CI
  --prerelease {alpha,beta,rc}, -pr {alpha,beta,rc}
                        choose type of prerelease
  --increment {MAJOR,MINOR,PATCH}
                        manually specify the desired increment
```

## Configuration

### `tag_format`

Used to read the format from the git tags, and also to generate the tags.

Supports 2 types of formats, a simple and a more complex.

```bash
cz bump --tag_format="v$version"
```

```bash
cz bump --tag_format="v$minor.$major.$patch$prerelease"
```

In your `pyproject.toml` or `.cz.toml`

```toml
[tool.commitizen]
tag_format = "v$minor.$major.$patch$prerelease"
```

Or in your `.cz` (TO BE DEPRECATED)

```
[commitizen]
tag_format = v$minor.$major.$patch$prerelease
```

The variables must be preceded by a `$` sign.

Suppported variables:

| Variable      | Description                                |
| ------------- | ------------------------------------------ |
| `$version`    | full generated version                     |
| `$major`      | MAJOR increment                            |
| `$minor`      | MINOR increment                            |
| `$patch`      | PATCH increment                            |
| `$prerelease` | Prerelase (alpha, beta, release candidate) |

---

### `files`

Used to identify the files which should be updated with the new version.
It is also possible to provide a pattern for each file, separated by colons (`:`).

Commitizen will update it's configuration file automatically (`pyproject.toml`, `.cz`) when bumping,
regarding if the file is present or not in `files`.

Some examples

`pyproject.toml` or `.cz.toml`

```toml
[tool.commitizen]
files = [
    "src/__version__.py",
    "setup.py:version"
]
```

`.cz` (TO BE DEPRECATED)

```
[commitizen]
files = [
    "src/__version__.py",
    "setup.py:version"
    ]
```

In the example above, we can see the reference `"setup.py:version"`.
This means that it will find a file `setup.py` and will only make a change
in a line containing the `version` substring.

---

### `bump_message`

Template used to specify the commit message generated when bumping

defaults to: `bump: version $current_version → $new_version`

| Variable           | Description                         |
| ------------------ | ----------------------------------- |
| `$current_version` | the version existing before bumping |
| `$new_version`     | version generated after bumping     |

Some examples

`pyproject.toml` or `.cz.toml`

```toml
[tool.commitizen]
bump_message = "release $current_version → $new_version [skip-ci]"
```

`.cz` (TO BE DEPRECATED)

```
[commitizen]
bump_message = release $current_version → $new_version [skip-ci]
```

## Custom bump

Read the [customizing section](./customization.md).

[pep440]: https://www.python.org/dev/peps/pep-0440/
[semver]: https://semver.org/
