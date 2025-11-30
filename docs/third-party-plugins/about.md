# What are third-party plugins?

Third-party plugins are a way to extend Commitizen with additional customized features.

These plugins are available as PyPI packages (installable with `pip`).

!!! note
    New plugins are welcome! Once you published your plugins, please send us a PR to update this page.

!!! note "Historical notes"
    This section was originally called "Third-Party Commitizen Templates", but has been renamed to "Third-Party Commitizen Plugins" to better reflect the content.

## Plugin features

<!-- TODO: provide more details about the features -->
<!-- We can move the details from customization pages to here -->

### Commit message convention

Includes the rules to validate and generate commit messages.

### Version scheme

Includes the rules to generate version numbers.

### Version provider

Read and write version from data sources.

### Changelog format

Generate changelog in customized formats.

<!-- TODO: complete the following section -->
<!-- ## How do I create a new plugin? -->

## How to help us update the list of plugins?

Please document what features the plugin provides:

- a convention
- a scheme
- a provider
- a `changelog_format`

Of course, a plugin can provide multiple features.
You may have noticed that `commitizen` itself can be viewed as a plugin that provides all the above features.

Please see [cz-path](./cz-path.md) for a detailed example.

## New plugin documentation template

    # [Package name](https://github.com/author/package-name)

    <!-- Description of the plugin. -->

    <!-- What features does the plugin provide? -->

    ## Installation

    ```sh
    pip install package-name
    ```

    ## Usage

    ```sh
    cz --name package-name commit
    ```

    ## Example

    <!-- Example usage of the plugin. -->
