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
    bump_commit_filter_pattern = "^(feat|fix)\\(library-b\\)(!)?:"
    update_changelog_on_bump = true

    [tool.commitizen.customize]
    changelog_pattern = "^(feat|fix)\\(library-b\\)(!)?:"
    ```

    ```toml
    # library-z/.cz.toml
    [tool.commitizen]
    name = "cz_customize"
    version = "0.0.0"
    tag_format = "${version}-library-z"
    ignored_tag_formats = ["${version}-library-*"] # Avoid noise from other tags
    bump_commit_filter_pattern = "^(feat|fix)\\(library-z\\)(!)?:"
    update_changelog_on_bump = true

    [tool.commitizen.customize]
    changelog_pattern = "^(feat|fix)\\(library-z\\)(!)?:"
    ```

3. **Bump each component independently**

    ```sh
    cz --config library-b/.cz.toml bump --yes
    cz --config library-z/.cz.toml bump --yes
    ```


## Bump and changelog per component

To filter the correct commits for each component, you'll need to define a strategy.

For example:

- Trigger the pipeline based on the changed path. This can have some downsides, as you'll rely on the developer not including files from unrelated components.
    - [GitHub Actions](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore) uses `path`
    - [Jenkins](https://www.jenkins.io/doc/book/pipeline/syntax/#built-in-conditions) uses `changeset`
    - [GitLab](https://docs.gitlab.com/ee/ci/yaml/#ruleschanges) uses `rules:changes`
- Filter commits by a specific pattern in the commit message (recommended)


### Example with scope in conventional commits

In this example, we want `library-b`'s bump calculation and changelog to only
include commits that use the `library-b` scope. These are filtered separately:

- `bump_commit_filter_pattern` selects the commits used to calculate the version
  bump.
- `changelog_pattern` selects the commits included in the changelog.

The `library-b` configuration in step 2 sets both patterns to ensure that the
bump calculation and changelog include the same component-specific commits.

With these patterns, a commit message like the following would affect
`library-b`'s bump calculation and be included in its changelog:

```text
fix(library-b): Some awesome message
```
