Feel free to send a PR to update this file if you find anything useful. 🙇

## Environment

- Python `>=3.9`
- [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) `>=2.0.0`

## Useful commands

Please check the [pyproject.toml](https://github.com/commitizen-tools/commitizen/blob/master/pyproject.toml) for a comprehensive list of commands.

### Code Changes

```bash
# Ensure you have the correct dependencies
poetry install

# Make ruff happy
poetry format

# Check if ruff and mypy are happy
poetry lint

# Check if mypy is happy in python 3.9
mypy --python-version 3.9

# Run tests in parallel.
pytest -n auto # This may take a while.
pytest -n auto <test_suite>
```

### Documentation Changes

```bash
# Build the documentation locally and check for broken links
poetry doc
```
