# Architecture Overview

This page is a map of Commitizen's subsystems and extension points. It is aimed
at contributors (human or AI) who are about to change code and need to know
where things live and how they fit together.

For end-user concepts, see the [Commands](../commands/init.md) and
[Configuration](../config/configuration_file.md) sections.

## Top-level layout

```
commitizen/
├── cli.py                  # CLI entry point and argument parsing (uses decli)
├── commands/               # One module per CLI subcommand (commit, bump, changelog, ...)
├── config/                 # Configuration discovery, parsing, and base classes
├── providers/              # Version providers (where to read/write the version)
├── changelog_formats/      # Changelog file format handlers (markdown, asciidoc, ...)
├── cz/                     # Built-in commit conventions (conventional_commits, jira, customize)
├── version_schemes.py      # Version schemes (pep440, semver, semver2)
├── tags.py                 # Tag format parsing and matching
├── changelog.py            # Changelog generation engine
├── bump.py                 # Version-bump engine
├── defaults.py             # Default settings and the Settings TypedDict
├── exceptions.py           # CLI-facing exception types and exit codes
├── out.py                  # Standard output helpers
├── git.py                  # Git wrapper used by all commands
├── hooks.py                # Pre/post bump hook execution
└── templates/              # Built-in Jinja2 templates for changelog rendering
```

## Extension points

Commitizen is plugin-friendly. Four kinds of extensions can be registered by
external packages via Python entry points; the built-in implementations use
the same mechanism.

| Kind | Entry-point group | Built-ins registered in `pyproject.toml` | Base class / Protocol |
|---|---|---|---|
| Commit convention | `commitizen.plugin` | `cz_conventional_commits`, `cz_jira`, `cz_customize` | `commitizen/cz/base.py:BaseCommitizen` |
| Version provider | `commitizen.provider` | `cargo`, `commitizen`, `composer`, `npm`, `pep621`, `poetry`, `scm`, `uv` | `commitizen/providers/base_provider.py:VersionProvider` |
| Version scheme | `commitizen.scheme` | `pep440`, `semver`, `semver2` | `commitizen/version_schemes.py:VersionProtocol` |
| Changelog format | `commitizen.changelog_format` | `markdown`, `asciidoc`, `textile`, `restructuredtext` | `commitizen/changelog_formats/base.py:BaseFormat` |

Each kind is loaded lazily via `importlib.metadata.entry_points(...)`. To add
a new built-in implementation you register it in `pyproject.toml` under the
appropriate `[project.entry-points."..."]` table.

End-user documentation for these extension points lives elsewhere — see
[Version Provider](../config/version_provider.md),
[Customized Python Class](../customization/python_class.md), and
[Changelog Template](../customization/changelog_template.md). This page
focuses on where the source lives and how it is wired together.

## Configuration layering

Configuration is discovered, parsed, and exposed as a `Settings` TypedDict.

1. **Discovery** — `commitizen/config/__init__.py:read_cfg` searches the
   working directory (and the git project root when different) for known
   config files in a defined order (see
   `commitizen/defaults.py:CONFIG_FILES`).
2. **Format-specific parsing** — `commitizen/config/factory.py:create_config`
   dispatches to one of:
   - `commitizen/config/toml_config.py:TomlConfig` (TOML; includes
     `pyproject.toml` under `[tool.commitizen]`)
   - `commitizen/config/json_config.py:JsonConfig`
   - `commitizen/config/yaml_config.py:YAMLConfig`
3. **Defaults merge** — every parser inherits from
   `commitizen/config/base_config.py:BaseConfig`, which starts from
   `commitizen/defaults.py:DEFAULT_SETTINGS` and overlays the user values.
4. **Consumption** — commands read `config.settings[...]`; providers and
   formats receive the live `BaseConfig` so they can react to settings such
   as `encoding`, `tag_format`, and `version_scheme`.

The `Settings` TypedDict in `defaults.py` is the authoritative list of
recognized keys. Adding a new setting almost always means touching this file.

## Command flow

`cli.py` parses `argv` with [decli](https://github.com/woile/decli), resolves
the chosen subcommand to a class under `commitizen/commands/`, then
instantiates and calls it. A typical command:

1. Reads `config.settings`.
2. Resolves dependencies (provider, scheme, changelog format) via the
   `get_*` helpers in the respective subpackages.
3. Does its work, surfacing user-visible text through `commitizen/out.py`
   and errors through `commitizen/exceptions.py` (each exception carries an
   exit code defined in `commitizen/exceptions.py` and documented in
   [Exit Codes](../exit_codes.md)).

`cz commit` and `cz bump` are the most stateful commands — they call `git`
through `commitizen/git.py`, run user-defined `pre_bump_hooks`/`post_bump_hooks`
via `commitizen/hooks.py`, and may mutate version files through the active
provider.

## Templates and changelog rendering

Changelog rendering uses Jinja2. Built-in templates live under
`commitizen/templates/`. The template loader is a `ChoiceLoader` whose first
loader is `FileSystemLoader(".")` and whose second loader is provided by the
active commit-convention class (default: a `PackageLoader` for built-in
templates), so a repository can override any built-in template by placing a
file of the same name at the project root or in the configured template
directory.

## Tests mirror the source tree

Tests are organized to mirror the source modules:

| Source | Test |
|---|---|
| `commitizen/providers/*` | `tests/providers/`, `tests/test_factory.py` |
| `commitizen/changelog_formats/*` | `tests/test_changelog_format_*.py`, `tests/test_changelog_formats.py` |
| `commitizen/version_schemes.py` | `tests/test_version_schemes.py`, `tests/test_version_scheme_*.py` |
| `commitizen/commands/*` | `tests/commands/`, `tests/test_cli/` |
| `commitizen/config/*` | `tests/test_conf.py` |
| `commitizen/bump.py` | `tests/test_bump_*.py` |
| `commitizen/changelog.py` | `tests/test_changelog.py`, `tests/test_incremental_build.py` |
| `commitizen/tags.py` | `tests/test_tags.py` |

When you add or modify a subsystem, the targeted test file is usually
obvious from this mirror. The
[targeted-test map for agents](agents/validation.md#targeted-test-map)
captures the most useful selectors.
