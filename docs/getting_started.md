## Initialize commitizen

If it's your first time, you'll need to create a commitizen configuration file.

The assistant utility will help you set up everything

```sh
cz init
```

Alternatively, create a file `.cz.toml` or `cz.toml` in your project's directory.

```toml
[tool.commitizen]
version = "0.1.0"
update_changelog_on_bump = true
```

## Usage

### Bump version

```sh
cz bump
```

This command will bump your project's version, and it will create a tag.

Because of the setting `update_changelog_on_bump`, bump will also create the **changelog**.
You can also [update files](./commands/bump.md#version_files).
You can configure the [version scheme](./commands/bump.md#version_scheme) and [version provider](./config.md#version-providers).

There are many more options available, please read the docs for the [bump command](./commands/bump.md).

### Committing

Run in your terminal

```bash
cz commit
```

or the shortcut

```bash
cz c
```

#### Sign off the commit

Run in the terminal

```bash
cz commit -- --signoff
```

or the shortcut

```bash
cz commit -- -s
```

### Get project version

Running `cz version` will return the version of commitizen, but if you want
your project's version you can run:

```sh
cz version -p
```

This can be useful in many situations, where otherwise, you would require a way
to parse the version of your project. Maybe it's simple if you use a `VERSION` file,
but once you start working with many different projects, it becomes tricky.

A common example is, when you need to send to slack, the changes for the version that you
just created:

```sh
cz changelog --dry-run "$(cz version -p)"
```

### Integration with Pre-commit

Commitizen can lint your commit message for you with `cz check`.

You can integrate this in your [pre-commit](https://pre-commit.com/) config with:

```yaml
---
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: master
    hooks:
      - id: commitizen
      - id: commitizen-branch
        stages: [push]
      - id: commitizen-prepare-commit-msg
        stages: [prepare-commit-msg]
```

After the configuration is added, you'll need to run:

```sh
pre-commit install --hook-type commit-msg --hook-type pre-push --hook-type prepare-commit-msg
```

If you aren't using both hooks, you needn't install both stages.

| Hook              | Recommended Stage |
| ----------------- | ----------------- |
| commitizen        | commit-msg        |
| commitizen-branch | pre-push          |
| commitizen-prepare-commit-msg | prepare-commit-msg |

Note that pre-commit discourages using `master` as a revision, and the above command will print a warning. You should replace the `master` revision with the [latest tag](https://github.com/commitizen-tools/commitizen/tags). This can be done automatically with:

```sh
pre-commit autoupdate
```

Read more about the `check` command [here](commands/check.md).
