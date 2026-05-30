# Playbook: Add a Version Provider

A version provider tells Commitizen where to read and write the project's version (e.g., `pyproject.toml` for PEP 621, `Cargo.toml` for Cargo, `package.json` for npm). End-user documentation: [Version Provider](../../../config/version_provider.md).

Architectural context: [Architecture § Extension points](../../architecture.md#extension-points).

## Trigger

- "Add support for `<ecosystem>` version files."
- "Read the version from `<file>` instead of asking the user."
- Issue or feature request mentions a packaging system that is not in the list of built-ins (`cargo`, `commitizen`, `composer`, `npm`, `pep621`, `poetry`, `scm`, `uv`).

## Read first

- `commitizen/providers/__init__.py` — registration helper `get_provider`, entry-point group `commitizen.provider`, default provider name.
- `commitizen/providers/base_provider.py` — `VersionProvider`, `FileProvider`, `JsonProvider`, `TomlProvider` base classes.
- An existing provider that resembles your target:
    - JSON file with non-standard layout: `commitizen/providers/composer_provider.py`
    - TOML file with multi-file updates: `commitizen/providers/uv_provider.py`
    - SCM tag-based, no file write: `commitizen/providers/scm_provider.py`
- Test for the closest existing provider: `tests/providers/test_<name>_provider.py`.
- `commitizen/config/base_config.py:BaseConfig` — what your provider's `__init__(config)` will receive.

## Steps

1. **Create the provider module** at `commitizen/providers/<name>_provider.py`. Subclass the closest base:
    - `TomlProvider` if your file is TOML and `[project].version` is sufficient — override only `get`/`set` if the version lives at a different path.
    - `JsonProvider` for JSON files; same override pattern.
    - `FileProvider` directly when the format is neither TOML nor JSON.
    - `VersionProvider` when there is no file (e.g., SCM-tag-based).
2. **Honor the configured encoding** for every file read and write — call `self._get_encoding()` (provided by `FileProvider`) rather than relying on system defaults. See `commitizen/providers/base_provider.py` for examples.
3. **Register the built-in** by adding one line to `pyproject.toml` under `[project.entry-points."commitizen.provider"]`:

   ```toml
   <name> = "commitizen.providers:<NameProvider>"
   ```

4. **Export the class** from `commitizen/providers/__init__.py`: import it and add it to `__all__`.
5. **Add tests** at `tests/providers/test_<name>_provider.py`. The existing tests demonstrate the patterns — most use `pytest-regressions` for file snapshots and `pytest-mock` to substitute the working directory.
6. **Update user docs** at `docs/config/version_provider.md` — add a row to the providers table and an example block if the configuration is non-trivial.
7. **Re-run the editable install** so the new entry point is picked up:

   ```bash
   uv sync --frozen --group base --group test --group linters
   ```

## Validate

```bash
uv run pytest tests/providers/test_<name>_provider.py tests/test_factory.py -n auto
uv run poe lint
uv run poe doc:build      # if docs/config/version_provider.md changed
uv run poe all            # final pre-push (PR template requirement)
```

## Pitfalls

- **Forgetting `pyproject.toml` registration** — the provider class will exist but `cz bump` will raise `VersionProviderUnknown` because `get_provider` looks it up by entry point, not by import path.
- **Hardcoded `open(path)`** — drops the user's configured encoding. Use `self._get_encoding()` and `Path.read_text(encoding=...)`.
- **Mutating files outside `set_version`** — providers should be idempotent and side-effect-free on `get_version`. Multi-file updates (like `UvProvider` updating both `pyproject.toml` and `uv.lock`) belong inside `set_version`.
- **Not testing the missing-file path** — `cz bump --get-next` runs `get_version` on a fresh checkout. Make sure your provider returns a reasonable default or raises a clear exception when its file is absent.
- **Cross-platform line endings** — write with `Path.write_text(...)` and add a trailing newline; do not assume `\n`.

## Stop and ask if

- The packaging ecosystem requires authentication to discover the version (e.g., reading from a registry). Network-dependent providers are out of scope for built-ins; suggest packaging it as a third-party plugin.
- The version is split across two unrelated files with no clear "primary" source.
- The setting would require a new key in the `Settings` TypedDict (`commitizen/defaults.py`) — that is a config schema change, surface it in the issue.
