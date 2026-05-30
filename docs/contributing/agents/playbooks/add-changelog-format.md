# Playbook: Add a Changelog Format

A changelog format handles parsing and rendering a `CHANGELOG.<ext>` file in a specific markup language. End-user documentation: [Changelog command](../../../commands/changelog.md). Built-ins are `markdown` (default), `asciidoc`, `textile`, `restructuredtext`.

Architectural context: [Architecture § Extension points](../../architecture.md#extension-points).

## Trigger

- "Support `<markup>` changelogs."
- A user wants `cz changelog` to emit something other than Markdown.
- An incremental-changelog use case fails because the user's existing `CHANGELOG` file is not Markdown.

## Read first

- `commitizen/changelog_formats/__init__.py` — `ChangelogFormat` Protocol, entry-point group `commitizen.changelog_format`, `KNOWN_CHANGELOG_FORMATS` registry, `_guess_changelog_format` extension-based fallback.
- `commitizen/changelog_formats/base.py:BaseFormat` — abstract implementation; you only need to override `parse_version_from_title` and `parse_title_level`.
- A close-match existing format:
    - Heading-prefix-based: `commitizen/changelog_formats/markdown.py` (uses `#`, `##` prefixes).
    - Underline-based: `commitizen/changelog_formats/restructuredtext.py` (uses `===`, `---` lines).
- `commitizen/templates/` — Jinja2 templates named `CHANGELOG.<ext>.j2` control rendering.
- `tests/test_changelog_format_<name>.py` — every format has parity tests; copy the closest one.

## Steps

1. **Create the format module** at `commitizen/changelog_formats/<name>.py`. Subclass `BaseFormat`. Set the class attributes:
    - `extension: ClassVar[str]` — primary file extension (no dot).
    - `alternative_extensions: ClassVar[set[str]]` — other accepted extensions for the same format.
2. **Implement two methods**:
    - `parse_version_from_title(line: str) -> VersionTag | None` — given one line, return a `VersionTag` if the line is a release heading.
    - `parse_title_level(line: str) -> int | None` — return the heading level (1, 2, 3, ...) if the line is a heading. The base class `BaseFormat.get_metadata_from_file` walks the file once and calls both methods per line.
3. **Add the Jinja2 template** at `commitizen/templates/CHANGELOG.<ext>.j2`. Mirror the structure of `CHANGELOG.md.j2` — same blocks, different markup. Make sure the loops over `tree`, `entries`, and `change_type` match.
4. **Register the built-in** in `pyproject.toml` under `[project.entry-points."commitizen.changelog_format"]`:

   ```toml
   <name> = "commitizen.changelog_formats.<name>:<Name>"
   ```

5. **Add tests** at `tests/test_changelog_format_<name>.py`. Copy the closest existing test file and adapt the fixtures.
6. **Update the cross-format suite** `tests/test_changelog_formats.py` if it parametrizes over all formats — add the new one to its lists.
7. **Update user docs** at `docs/commands/changelog.md` and `docs/customization/changelog_template.md` — list the new format and show how to opt in via `changelog_format`.
8. **Re-run the install** so the entry point registers:

   ```bash
   uv sync --frozen --group base --group test --group linters
   ```

## Validate

```bash
uv run pytest tests/test_changelog_format_<name>.py tests/test_changelog_formats.py tests/test_changelog.py tests/test_incremental_build.py -n auto
uv run poe lint
uv run poe doc:build      # if docs changed
uv run poe all            # final pre-push
```

## Pitfalls

- **`KNOWN_CHANGELOG_FORMATS` is populated at import time** from entry points, so you must re-run `uv sync` after editing `pyproject.toml` before tests can see your new format.
- **Forgetting `alternative_extensions`** — `_guess_changelog_format` uses both `extension` and `alternative_extensions` when the user does not set `changelog_format` explicitly. If a user has `CHANGELOG.<alt-ext>`, your format will not auto-detect without it.
- **Template encoding** — Jinja2 reads templates with the active encoding; keep them ASCII-safe or test with non-UTF-8 `encoding` settings.
- **Heading regex anchoring** — match the whole line (`^...$`) when the markup is line-anchored (Markdown headings); a substring match will pick up non-heading lines that mention `unreleased`.
- **Snapshot updates** — many changelog tests use `pytest-regressions`. See the [update-snapshots playbook](update-snapshots.md) when output intentionally changes.

## Stop and ask if

- The target format requires structured metadata that does not fit the `parse_title_*` Protocol (e.g., front-matter in YAML).
- The format implies a fundamentally different rendering tree (e.g., one file per release) — that is a bigger change than a format addition.
