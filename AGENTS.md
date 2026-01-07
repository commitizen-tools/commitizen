# AGENTS instructions

## Purpose

This file provides **project-specific guidance for AI agents** (and other automated tools) working on the `commitizen` repository.
Follow these instructions in addition to any higher-level system or tool rules.

## Project Overview

- **Project**: `commitizen` - a tool to help enforce and automate conventional commits, version bumps, and changelog generation.
- **Primary language**: Python (library + CLI).
- **Key entrypoints**:
  - `commitizen/cli.py` - main CLI implementation.
  - `commitizen/commands/` - subcommands such as `bump`, `commit`, `changelog`, `check`, etc.
  - `commitizen/config/` - configuration discovery and loading.
  - `commitizen/providers/` - version providers (e.g., `pep621`, `poetry`, `npm`, `uv`).

## General Expectations

- **Preserve public behavior and CLI UX.**
- **Avoid breaking changes** (APIs, CLI flags, exit codes) unless explicitly requested.
- **Keep changes small and focused.**
- **Update or add tests/docs** when you change user-facing behavior.

## How to Explore and Validate Changes

- **Code entrypoints**:
  - CLI behavior: `commitizen/cli.py` and `commitizen/commands/`.
  - Config resolution: `commitizen/config/factory.py` and config modules.
  - Bump/changelog/versioning: `commitizen/bump.py`, `commitizen/changelog.py`, `commitizen/version_schemes.py`, `commitizen/providers/`.
- **Docs to consult** (before larger changes):
  - `docs/README.md`
  - `docs/contributing.md`
  - `docs/commands/` and `docs/config/`
- **Tests**:
  - Prefer targeted runs, e.g. `uv run pytest tests/test_cli.py` or a specific `tests/commands/` file.

## Coding Guidelines (for AI tools)

- **Style**: Follow patterns in nearby code; keep functions focused.
- **Types**: Preserve or improve existing type hints.
- **Errors**: Prefer `commitizen/exceptions.py` error types; keep messages clear for CLI users.
- **Output**: Use `commitizen/out.py`; do not add noisy logging.

## Common Task Pointers

- **CLI commands**: edit `commitizen/commands/<name>.py`, wire via `commitizen/cli.py`, and adjust `tests/commands/` + `docs/commands/`.
- **Version bumps / changelog**: use `commitizen/bump.py`, `commitizen/changelog.py`, `commitizen/version_schemes.py`, and `commitizen/providers/` (+ matching tests).
- **Config resolution**: use `commitizen/config/factory.py` and config modules; update `tests/test_conf.py` and related tests.

## When Unsure

- Prefer **reading tests and documentation first** to understand the expected behavior.
- When behavior is ambiguous, **assume backward compatibility** with current tests and docs is required.
