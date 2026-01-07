## Is this project affiliated with the [cz-cli][cz-cli] project?

**It is not affiliated.**

Both are used for similar purposes, parsing commits, generating changelog and version we presume.
Our Commitizen project is written in python to make integration easier for python projects, whereas [cz-cli][cz-cli] is written in JavaScript and serves the JS packages.

<!-- TODO: Add more details about the differences between Commitizen and cz-cli -->

They differ a bit in design, not sure if cz-cli does any of this, but these are some things you can do with our Commitizen:

- create custom rules, version bumps and changelog generation. By default, we use the popular conventional commits (I think cz-cli allows this).
- single package, install one thing and it will work. cz-cli is a monorepo, but you have to install different dependencies as far as I know.
- pre-commit integration
- works on any language project, as long as you create the `.cz.toml` or `cz.toml` file.

Where do they cross paths?

If you are using conventional commits in your git history, then you could swap one with the other in theory.

Regarding the name, [cz-cli][cz-cli] came first, they used the word Commitizen first. When this project was created originally, the creator read "be a good commitizen", and thought it was just a cool word that made sense, and this would be a package that helps you be a good "commit citizen".

[cz-cli]: https://github.com/commitizen/cz-cli
