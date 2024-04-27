# Configuring commitizen in a monorepo

This tutorial assumes the monorepo layout is designed with multiple components that can be released independently of each
other, it also assumes that conventional commits with scopes are in use. Some suggested layouts:

```
.
├── library-b
│   └── .cz.toml
└── library-z
    └── .cz.toml
```

```
src
├── library-b
│   └── .cz.toml
└── library-z
    └── .cz.toml
```

Each component will have its own changelog, commits will need to use scopes so only relevant commits are included in the
appropriate change log for a given component. Example config and commit for `library-b`

```toml
[tool.commitizen]
name = "cz_customize"
version = "0.0.0"
tag_format = "${version}-library-b" # the component name can be a prefix or suffix with or without a separator
update_changelog_on_bump = true

[tool.commitizen.customize]
changelog_pattern = "^(feat|fix)\\(library-b\\)(!)?:" #the pattern on types can be a wild card or any types you wish to include
```

example commit message for the above

`fix:(library-b) Some awesome message`

If the above is followed and the `cz bump --changelog` is run in the directory containing the component the changelog
should be generated in the same directory with only commits scoped to the component.
