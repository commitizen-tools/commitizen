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

### Why are `revert` and `chore` valid types in the check pattern of cz conventional_commits but not types we can select?

`revert` and `chore` are added to the "pattern" in `cz check` in order to prevent backward errors, but officially they are not part of conventional commits, we are using the latest [types from Angular](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type) (they used to but were removed).
However, you can create a customized `cz` with those extra types. (See [Customization](https://commitizen-tools.github.io/commitizen/customization/)

See more discussion in issue [#142](https://github.com/commitizen-tools/commitizen/issues/142) and [#36](https://github.com/commitizen-tools/commitizen/issues/36)

### How to revert a bump?

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
- works on any language project, as long as you create the `.cz.toml` file.

Where do they cross paths?

If you are using conventional commits in your git history, then you could swap one with the other in theory.

Regarding the name, [cz-js][cz-js] came first, they used the word commitizen first. When this project was created originally, the creator read "be a good commitizen", and thought it was just a cool word that made sense, and this would be a package that helps you be a good "commit citizen".

[cz-js]: https://github.com/commitizen/cz-cli
