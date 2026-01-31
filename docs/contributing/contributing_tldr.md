# Contributing TL;DR

Feel free to send a PR to update this file if you find anything useful. 🙇

## Environment

- Python `>=3.10`
- [uv](https://docs.astral.sh/uv/getting-started/installation/) `>=0.9.0`

## Useful commands

Please check the [pyproject.toml](https://github.com/commitizen-tools/commitizen/blob/master/pyproject.toml) for a comprehensive list of commands.

### Code Changes

```bash
# Ensure you have the correct dependencies
uv sync --dev --frozen

# Make ruff happy
uv run poe format

# Check if ruff and mypy are happy
uv run poe lint

# Check if mypy is happy in python 3.10
mypy --python-version 3.10

# Run tests in parallel.
pytest -n auto # This may take a while.
pytest -n auto <test_suite>
```

### Documentation Changes

```bash
# Build the documentation locally and check for broken links
uv run poe doc
```
