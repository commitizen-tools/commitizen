## Support for PEP621

PEP621 establishes a `[project]` definition inside `pyproject.toml`

```toml
[project]
name = "spam"
version = "2020.0.0"
```

Commitizen **won't** use the `project.version` as a source of truth because it's a
tool aimed for any kind of project.

If we were to use it, it would increase the complexity of the tool. Also why
wouldn't we support other project files like `cargo.toml` or `package.json`?

Instead of supporting all the different project files, you can use `version_files`
inside `[tool.commitizen]`, and it will cheaply keep any of these project files in sync

```toml
[tool.commitizen]
version = "2.5.1"
version_files = [
    "pyproject.toml:^version",
    "cargo.toml:^version",
    "package.json:\"version\":"
]
```
