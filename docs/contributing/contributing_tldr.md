# Contributing TL;DR

Feel free to send a PR to update this file if you find anything useful. 🙇

For prerequisites and initial setup, see [Contributing to Commitizen](contributing.md#prerequisites-setup).

## Command Cheat Sheet

See [pyproject.toml](https://github.com/commitizen-tools/commitizen/blob/master/pyproject.toml) for the full list of poe tasks.

```bash
# Format code (ruff check --fix + ruff format)
uv run poe format

# Lint (ruff check + mypy)
uv run poe lint

# Check mypy against a specific Python version
uv run mypy --python-version 3.10

# Run tests in parallel (may take a while)
uv run pytest -n auto
uv run pytest -n auto <test_suite>

# Build and preview docs locally
uv run poe doc

# Run everything (format + lint + check-commit + coverage)
uv run poe all
```
