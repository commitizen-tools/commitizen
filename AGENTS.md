# AGENTS instructions

## Purpose

This file provides **project-specific guidance for AI agents** (and other automated tools) working on the `commitizen` repository.
Follow these instructions in addition to any higher-level system or tool rules.

## Project Overview

- **Project**: `commitizen` - a tool to help enforce and automate conventional commits, version bumps, and changelog generation.
- **Primary language**: Python (library + CLI).
- **Cross-platform**: Tests run on Linux, macOS, and Windows. Avoid POSIX-only assumptions in code (paths, subprocesses, line endings).
- **Key entrypoints**:
  - `commitizen/cli.py` - main CLI implementation.
  - `commitizen/commands/` - subcommands such as `bump`, `commit`, `changelog`, `check`, etc.
  - `commitizen/config/` - configuration discovery and loading.
  - `commitizen/providers/` - version providers (e.g., `pep621`, `poetry`, `npm`, `uv`).
- **Config sources**: `pyproject.toml` (project config, poe tasks, ruff, ty), `.pre-commit-config.yaml` (hooks), `.github/workflows/` (CI).

## General Expectations

- **Preserve public behavior and CLI UX** — no breaking changes to APIs, CLI flags, or exit codes unless explicitly requested.
- **Update or add tests/docs** when you change user-facing behavior.
- **Commit messages** must follow [Conventional Commits](https://www.conventionalcommits.org/) (enforced by commitizen itself).

## Setup and Validation

### Bootstrap

```bash
uv sync --frozen --group base --group test --group linters
```

### Local commands

- **Format**: `uv run poe format` (runs `ruff check --fix` then `ruff format`)
- **Lint**: `uv run poe lint` (runs `ruff check` then `ty check`)
- **Test**: `uv run poe test` (runs `pytest -n auto`)
- **CI-equivalent**: `uv run poe ci` (commit check + pre-commit hooks via `prek` + test with coverage)
- **Full local check**: `uv run poe all` (format + lint + check-commit + coverage)

Always run at least `uv run ruff check --fix . && uv run ruff format .` before pushing. CI will fail if the formatter modifies any files.

### CI pipeline

- CI runs `poe ci` on a matrix of Python 3.10–3.14 × ubuntu/macos/windows.
- Pre-commit hooks are defined in `.pre-commit-config.yaml` and run via `prek`.
- The matrix is **fail-fast**: inspect the earliest failing job that completed; others are cancelled.

### Common CI failure patterns

- **"Format Python code...Failed"**: Run `uv run poe format` and commit the result.
- **ty `invalid-argument-type` on TypedDict**: Dynamically-constructed dicts (e.g., from `pytest.mark.parametrize`) passed to TypedDict-typed params need `# type: ignore  # noqa: PGH003` or `cast()`.
- **"pathspec 'vX.Y.Z' did not match"**: `.pre-commit-config.yaml` pins a tag of this repo. Rebase onto master to pick up the tag.
- **`VersionProtocol` + `issubclass`**: This Protocol has non-method members (properties), so `issubclass()` raises `TypeError`. Use `hasattr` checks for runtime validation.

## What to Read Before Changing

| Changing... | Read first |
|---|---|
| CLI flags/arguments | `commitizen/cli.py`, `docs/commands/<cmd>.md`, `tests/test_cli/` |
| Bump logic | `commitizen/bump.py`, `commitizen/commands/bump.py`, `docs/commands/bump.md` |
| Changelog generation | `commitizen/changelog.py`, `commitizen/changelog_formats/`, `docs/commands/changelog.md` |
| Version schemes | `commitizen/version_schemes.py`, `tests/test_version_schemes.py` |
| Version providers | `commitizen/providers/`, `tests/test_providers.py`, `docs/config/version_provider.md` |
| Config resolution | `commitizen/config/`, `tests/test_conf.py`, `docs/config/` |
| Tag handling | `commitizen/tags.py`, `tests/test_tags.py` |
| Pre-commit / CI | `.pre-commit-config.yaml`, `.github/workflows/`, `pyproject.toml` (poe tasks) |

## Coding Guidelines

- **Types**: Preserve or improve existing type hints.
- **Errors**: Prefer `commitizen/exceptions.py` error types; keep messages clear for CLI users.
- **Output**: Use `commitizen/out.py`; do not add noisy logging.

## When Unsure

- Prefer **reading tests and documentation first** to understand the expected behavior.
- When behavior is ambiguous, **assume backward compatibility** with current tests and docs is required.
