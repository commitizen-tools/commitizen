# Configuring Commitizen in a monorepo

This tutorial assumes that your monorepo is structured with multiple components that can be released independently of each other.
It also assumes that you are using conventional commits with scopes.

Here is a step-by-step example using two libraries, `library-b` and `library-z`:

1. **Organize your monorepo**

    For example, you might have one of these layouts:

    ```shell-session
    .
    ├── library-b
    │   └── .cz.toml
    └── library-z
        └── .cz.toml
    ```

    ```shell-session
    src
    ├── library-b
    │   └── .cz.toml
    └── library-z
        └── .cz.toml
    ```

2. **Add a Commitizen configuration for each component**

    ```toml
    # library-b/.cz.toml
    [tool.commitizen]
    name = "cz_customize"
    version = "0.0.0"
    tag_format = "${version}-library-b" # the component name can be a prefix or suffix with or without a separator
    ignored_tag_formats = ["${version}-library-*"] # Avoid noise from other tags
    update_changelog_on_bump = true
    ```

    ```toml
    # library-z/.cz.toml
    [tool.commitizen]
    name = "cz_customize"
    version = "0.0.0"
    tag_format = "${version}-library-z"
    ignored_tag_formats = ["${version}-library-*"] # Avoid noise from other tags
    update_changelog_on_bump = true
    ```

3. **Bump each component independently**

    ```sh
    cz --config library-b/.cz.toml bump --yes
    cz --config library-z/.cz.toml bump --yes
    ```


## Changelog per component

To filter the correct commits for each component, you'll need to define a strategy.

For example:

- Trigger the pipeline based on the changed path. This can have some downsides, as you'll rely on the developer not including files from unrelated components.
    - [GitHub Actions](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore) uses `path`
    - [Jenkins](https://www.jenkins.io/doc/book/pipeline/syntax/#built-in-conditions) uses `changeset`
    - [GitLab](https://docs.gitlab.com/ee/ci/yaml/#ruleschanges) uses `rules:changes`
- Filter commits by a specific pattern in the commit message (recommended)


### Example with scope in conventional commits

In this example, we want `library-b`'s changelog to only include commits that use the `library-b` scope.
To achieve this, we configure Commitizen to match only commit messages with that scope.

Here is an example configuration for `library-b`:

```toml
[tool.commitizen.customize]
changelog_pattern = "^(feat|fix)\\(library-b\\)(!)?:" # the type pattern can be a wildcard or any types you wish to include
```

With this configuration, a commit message like the following would be included in `library-b`'s changelog:

```text
fix(library-b): Some awesome message
```
