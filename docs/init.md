To start using commitizen, the recommended approach is to run

```sh
cz init
```

This command will ask you for information about the project and will
configure the selected file type (`pyproject.toml`, `.cz.toml`, etc.).

The `init` will help you with

1. Choose a convention rules (`name`)
1. Choosing a version provider (`commitizen` or for example `Cargo.toml`)
1. Detecting your project's version
1. Detecting the tag format used
1. Choosing a version type (`semver` or `pep440`)
1. Whether to create the changelog automatically or not during bump
1. Whether you want to keep the major as zero while building alpha software.
