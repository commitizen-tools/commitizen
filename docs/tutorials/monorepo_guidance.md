# Configuring Commitizen in a monorepo

This tutorial assumes the monorepo layout is designed with multiple components that can be released independently of each
other, it also assumes that conventional commits with scopes are in use. Some suggested layouts:

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

Sample `.cz.toml` for each component:

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

And finally, to bump each of these:

```sh
cz --config library-b/.cz.toml bump --yes
cz --config library-z/.cz.toml bump --yes
```


## Changelog per component

In order to filter the correct commits for each component, you'll have to come up with a strategy.

For example:

- Trigger the pipeline based on the changed path, which can have some downsides, as you'll rely on the developer not including files from other files
    - [GitHub actions](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore) uses `path`
    - [Jenkins](https://www.jenkins.io/doc/book/pipeline/syntax/#built-in-conditions) uses `changeset`
    - [GitLab](https://docs.gitlab.com/ee/ci/yaml/#ruleschanges) uses `rules:changes`
- Filter certain pattern of the commit message (recommended)


### Example with scope in conventional commits

For this example, to include the message in the changelog, we will require commits to use a specific scope.
This way, only relevant commits will be included in the appropriate change log for a given component, and any other commit will be ignored.

Example config and commit for `library-b`:

```toml
[tool.commitizen.customize]
changelog_pattern = "^(feat|fix)\\(library-b\\)(!)?:" #the pattern on types can be a wild card or any types you wish to include
```

A commit message looking like this, would be included:

```
fix(library-b): Some awesome message
```
