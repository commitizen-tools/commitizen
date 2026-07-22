# Playbook: Deprecate a Public API

Commitizen ships a stable Python API on top of the CLI. Removing or renaming anything importable from `commitizen.*` is a breaking change. Use this playbook to add a deprecation window before removal in the next major version.

## Trigger

- "Rename `<old_name>` to `<new_name>`."
- "Remove the old `<symbol>`."
- "Change the signature of `<function>`."
- A refactor PR proposes removing a class, function, attribute, or module-level constant that is reachable via `import commitizen.<x>`.

## Read first

- `commitizen/changelog_formats/__init__.py` — example of a module-level `__getattr__` that warns and forwards (look at the `guess_changelog_format` → `_guess_changelog_format` deprecation).
- Any existing `warnings.warn(..., DeprecationWarning, stacklevel=2)` call site in the codebase — `grep -rn DeprecationWarning commitizen/`.
- `tests/test_deprecated.py` — pattern for asserting the warning is raised and the old path still works.
- `pyproject.toml:filterwarnings` — examples of deprecations that the test suite explicitly silences (currently `get_smart_tag_range`).

## Deprecation message convention

Match the phrasing used elsewhere in the codebase:

```
<old_name> is deprecated and will be removed in v<next_major>. Use <new_name> instead.
```

Example (from `commitizen/changelog_formats/__init__.py`):

```python
warnings.warn(
    "guess_changelog_format is deprecated and will be removed in v5. "
    "Use _guess_changelog_format instead.",
    DeprecationWarning,
    stacklevel=2,
)
```

## Steps

1. **Pick the deprecation shape** based on what you are changing:
    - **Renamed module-level symbol** → add a module `__getattr__` that returns the new symbol after issuing a `DeprecationWarning`. See `commitizen/changelog_formats/__init__.py` for the template.
    - **Renamed function/method** → keep the old name as a thin wrapper that warns and delegates.
    - **Changed function signature** → add a `typing.overload` for the old signature; internally route old usage to the new path and warn.
    - **Renamed class** → keep the old class as a subclass of the new one and emit a warning from `__init_subclass__` or `__init__`.
2. **Issue the warning** with `warnings.warn(<message>, DeprecationWarning, stacklevel=2)`. `stacklevel=2` points the warning at the caller, not at the wrapper.
3. **Decide the removal version**. Use the next major (current version is in `commitizen/__version__.py`). Put the version in the warning message and in the changelog entry.
4. **Add tests** in `tests/test_deprecated.py`:

   ```python
   def test_old_name_is_deprecated() -> None:
       with pytest.warns(DeprecationWarning, match="will be removed in v<N>"):
           result = commitizen.old_name(...)
       assert result == expected
   ```

5. **Silence the warning in the test suite** if the deprecated path is still exercised by unrelated tests. Add to `pyproject.toml:tool.pytest.filterwarnings`:

   ```toml
   "ignore:<old_name> is deprecated:DeprecationWarning",
   ```

6. **Update all internal callers** to use the new name. Run `git grep -n <old_name>` to find them all — search **docs**, **tests**, and `.github/` too, not just source.
7. **Update user docs** if the symbol is documented. For module-private symbols (leading underscore), this step is usually unnecessary.
8. **Note the removal target** in the PR description so the maintainers can track it.

## Validate

```bash
uv run pytest tests/test_deprecated.py -n auto
uv run pytest <subsystem tests>     # confirm new and old paths both work
uv run poe lint                     # mypy will warn if you import deprecated names internally
uv run poe all                      # final pre-push
git grep -n <old_name>              # zero hits expected outside the deprecation shim
```

## Pitfalls

- **Hard removal in a non-major release** — refuse. The deprecation must ship in version N, and the removal in N+1 (major).
- **Wrong `stacklevel`** — `stacklevel=1` points at the warning call itself and is unhelpful. Almost always use `2`.
- **Missing `filterwarnings` entry** — internal callers that still use the old name will turn the suite noisy (or break `-W error::DeprecationWarning` invocations).
- **Forgetting to grep docs/tests/CI** — the [PR scope rule](https://github.com/commitizen-tools/commitizen/blob/master/AGENTS.md) applies. A deprecation PR that leaves the old name referenced in `docs/` is incomplete.
- **`DeprecationWarning` is hidden by default** — Python suppresses it outside `__main__`. The PR description should mention how a downstream user will see it (test runners surface it, `-W default` shows it).

## Stop and ask if

- The symbol is documented as part of the public API and has no obvious successor. Propose a migration path in the issue first.
- Multiple symbols would deprecate at once with cross-dependencies — sequence them carefully so users can migrate in steps.
- The removal target would be the **same major** as the deprecation — that defeats the purpose of the window.
