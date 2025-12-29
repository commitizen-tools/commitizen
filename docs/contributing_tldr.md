Feel free to send a PR to update this file if you find anything useful. 🙇

## Environment

- Python `>=3.10`
- [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) `>=2.2.0`

## Useful commands

Please check the [pyproject.toml](https://github.com/commitizen-tools/commitizen/blob/master/pyproject.toml) for a comprehensive list of commands.

### Code Changes

```bash
# Make sure you have the latest version of poetry installed
poetry self update

# Ensure you have the correct dependencies, for nix user's see below
poetry install

# Make ruff happy
poetry format

# Check if ruff and mypy are happy
poetry lint

# Check if mypy is happy in python 3.10
mypy --python-version 3.10

# Run tests in parallel.
pytest -n auto # This may take a while.
pytest -n auto <test_suite>
```

### Documentation Changes

```bash
# Build the documentation locally and check for broken links
poetry doc
```

Also, we use [Lychee](https://lychee.cli.rs/) to check for broken links in the documentation.

```bash
# Check for broken links in the documentation
lychee .
```

### Nix Users

If you are using Nix, you can install poetry locally by running:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -U pip && pip install poetry
poetry install
```
