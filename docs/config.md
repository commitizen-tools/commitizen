# Configuration

**New!** Support for `pyproject.toml`

Add an entry to `pyproject.toml`.


    [tool.commitizen]
    name = "cz_conventional_commits"
    version = "0.1.0"
    files = [
        "src/__version__.py",
        "pyproject.toml"
    ]


Also, you can create in your project folder a file called `.cz`,
`.cz.cfg` or in your `setup.cfg` or if you want to configure the global
default in your user's home folder a `.cz` file with the following
information:

    [commitizen]
    name = cz_conventional_commits
    version = 0.1.0
    files = [
        "src/__version__.py",
        "pyproject.toml"
        ]

The extra tab at the end (`]`) is required.

## Settings

| Variable | Type | Default | Description |
| -------- | ---- | ------- | ----------- |
| `name` | `str` | `"cz_conventional_commits"` | Name of the commiting rules to use |
| `version` | `str` | `None` | Current version. Example: "0.1.2" |
| `files` | `list` | `[ ]` | Files were the version needs to be updated |
| `tag_format` | `str` | `None` | Format for the git tag, useful for old projects, that use a convention like `"v1.2.1"`. [See more](/bump#configuration) |
| `bump_message` | `str` | `None` | Create custom commit message, useful to skip ci. [See more](/bump#configuration) |
