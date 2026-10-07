# Configuring Commitizen in a monorepo

This tutorial assumes that your monorepo is structured with multiple components that can be released independently of each other.
It also assumes that you are using conventional commits with scopes.

Here is a step-by-step example using two libraries, `library-foo` and `library-alice`:

1. **Organize your monorepo**

For example, you might have one of these layouts:

```shell-session
.
├── library-foo
│   └── .cz.toml
└── library-alice
    └── .cz.toml
```

```shell-session
src
├── library-foo
│   └── .cz.toml
└── library-alice
    └── .cz.toml
```

2. **Add a Commitizen configuration for each component**

```toml
# library-foo/.cz.toml
[tool.commitizen]
name = "cz_customize"
version = "0.0.0"
tag_format = "${version}-library-foo" # the component name can be a prefix or suffix with or without a separator
ignored_tag_formats = ["${version}-library-(?!foo$).*"] # Avoid noise from other tags
update_changelog_on_bump = true
```

```toml
# library-alice/.cz.toml
[tool.commitizen]
name = "cz_customize"
version = "0.0.0"
tag_format = "${version}-library-alice"
ignored_tag_formats = ["${version}-library-(?!alice$).*"] # Avoid noise from other tags
update_changelog_on_bump = true
```

3. **Bump each component independently**

```sh
cz --config library-foo/.cz.toml bump --yes
cz --config library-alice/.cz.toml bump --yes
```

## Changelog Per Component

To filter the correct commits for each component, you'll need to define a strategy.

For example:

- Trigger the pipeline based on the changed path. This can have some downsides, as you'll rely on the developer not including files from unrelated components.
  - [GitHub Actions](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore) uses `path`
  - [Jenkins](https://www.jenkins.io/doc/book/pipeline/syntax/#built-in-conditions) uses `changeset`
  - [GitLab](https://docs.gitlab.com/ee/ci/yaml/#ruleschanges) uses `rules:changes`
- Filter commits by a specific pattern in the commit message (recommended)

### Filtering Commits

For advanced use cases, filter the commits passed to `version`, `bump` or `changelog` by implementing custom conventional commit rules.
See [Filter commits before bump and changelog generation](../customization/python_class.md#filter-commits-before-bump-and-changelog-generation)
