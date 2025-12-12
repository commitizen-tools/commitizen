
## Is this project affiliated with the [Commitizen JS][cz-js] project?

**It is not affiliated.**

Both are used for similar purposes, parsing commits, generating changelog and version we presume.
This one is written in python to make integration easier for python projects and the other serves the JS packages.

<!-- TODO: Add more details about the differences between Commitizen and Commitizen JS -->

They differ a bit in design, not sure if cz-js does any of this, but these are some things you can do with our Commitizen:

- create custom rules, version bumps and changelog generation. By default, we use the popular conventional commits (I think cz-js allows this).
- single package, install one thing and it will work. cz-js is a monorepo, but you have to install different dependencies as far as I know.
- pre-commit integration
- works on any language project, as long as you create the `.cz.toml` or `cz.toml` file.

Where do they cross paths?

If you are using conventional commits in your git history, then you could swap one with the other in theory.

Regarding the name, [cz-js][cz-js] came first, they used the word Commitizen first. When this project was created originally, the creator read "be a good commitizen", and thought it was just a cool word that made sense, and this would be a package that helps you be a good "commit citizen".

[cz-js]: https://github.com/commitizen/cz-cli
