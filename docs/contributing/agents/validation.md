# Validation Guide

How to verify a change to Commitizen without running the full CI matrix every
time. This page is the agent-facing counterpart to the human
[Contributing TL;DR](../contributing_tldr.md), focused on **which** selector
to run for a given change and **how** to recognize CI failures.

For the full poe command reference, see
[Contributing TL;DR](../contributing_tldr.md#command-cheat-sheet).

## Targeted test map

During iteration, prefer running only the tests that cover what you changed.
The full suite is for the final pre-push run. Tests mirror the source tree
(see [Architecture Overview § Tests mirror the source tree](../architecture.md#tests-mirror-the-source-tree));
the table below picks the most useful selectors.

| Changing... | Targeted selector |
|---|---|
| A version provider in `commitizen/providers/<name>_provider.py` | `uv run pytest tests/providers/test_<name>_provider.py -n auto` |
| The provider lookup or registration | `uv run pytest tests/providers/ tests/test_factory.py -n auto` |
| A changelog format in `commitizen/changelog_formats/<name>.py` | `uv run pytest tests/test_changelog_format_<name>.py tests/test_changelog_formats.py -n auto` |
| The changelog generation engine | `uv run pytest tests/test_changelog.py tests/test_incremental_build.py -n auto` |
| A version scheme | `uv run pytest tests/test_version_scheme_<name>.py tests/test_version_schemes.py -n auto` |
| Tag parsing / format | `uv run pytest tests/test_tags.py -n auto` |
| Bump logic | `uv run pytest "tests/test_bump_*.py" tests/commands/test_bump_command.py -n auto` |
| A CLI subcommand `commitizen/commands/<cmd>.py` | `uv run pytest tests/commands/test_<cmd>_command.py tests/test_cli/ -n auto` |
| CLI argument parsing (`commitizen/cli.py`) | `uv run pytest tests/test_cli/ tests/test_cli.py -n auto` |
| Configuration loading | `uv run pytest tests/test_conf.py -n auto` |
| A built-in commit convention (`commitizen/cz/<name>.py`) | `uv run pytest "tests/test_cz_<name>*.py" -n auto` |
| A deprecation | `uv run pytest tests/test_deprecated.py -n auto` plus the affected subsystem's tests |
| Exception classes | `uv run pytest tests/test_exceptions.py -n auto` |

Run mypy against the oldest supported Python version when adding type
annotations:

```bash
uv run mypy --python-version 3.10
```

This catches `typing-extensions` vs stdlib import issues that the default
mypy run does not flag.

## Choosing a final check

| Command | When to run | What it does |
|---|---|---|
| `uv run poe all` | Before pushing a PR (named in the PR template) | `format` -> `lint` -> `check-commit` -> `cover`. Auto-formats your files. |
| `uv run poe ci` | When you want to mirror CI exactly | `check-commit` -> `prek run --all-files` -> `cover`. Does **not** auto-format; fails if files need formatting. |
| `uv run poe doc:build` | After any docs change | `mkdocs build`. Prints broken-link warnings. Finite, not a server. |
| `uv run poe doc` | When iteratively editing docs | `mkdocs serve --livereload`. Runs until killed; not a verification step. |

Recommended sequence:

1. Iterate with targeted tests + `uv run poe format`.
2. Before push: `uv run poe all` (PR template requirement).
3. Optional: `uv run poe ci` to catch anything that `prek` will block in CI.
4. If docs changed: `uv run poe doc:build`.

## CI failure recipes

The CI matrix is fail-fast across Python 3.10–3.14 × ubuntu/macos/windows
(see `.github/workflows/`). Inspect the earliest failing job; the others are
cancelled.

### "Format Python code...Failed"

The `prek` formatting hook modified files. Run locally and commit the result:

```bash
uv run poe format
git add -u && git commit --amend --no-edit
```

### mypy `[arg-type]` on a TypedDict construction

Dynamically constructed dicts (e.g., from `pytest.mark.parametrize`) passed
to a TypedDict-typed parameter need an explicit ignore:

```python
@pytest.mark.parametrize("settings", [{"version_scheme": "pep440"}])
def test_x(settings: Settings) -> None:  # type: ignore[arg-type]
    ...
```

### `pathspec 'vX.Y.Z' did not match`

`.pre-commit-config.yaml` pins a specific tag of this repo as a hook source.
When your branch is older than that tag, the hook fails because the tag is
unknown. Fix by rebasing onto the latest master:

```bash
git fetch origin master
git rebase origin/master
```

### `VersionProtocol` + `issubclass` `TypeError`

`commitizen/version_schemes.py:VersionProtocol` has non-method members
(properties), so it cannot be passed to `issubclass()`. For runtime
validation, use `hasattr` checks against the concrete members or duck-type
the value instead of subclass-checking.

### Tests pass locally but fail in CI on Windows only

Most often a path-separator or encoding assumption:

- Use `pathlib.Path` and `Path(...).as_posix()` for string comparisons.
- Read files with `encoding=` (the convention is to honor
  `config.settings["encoding"]`; see
  `commitizen/providers/base_provider.py:_get_encoding`).
- Avoid hardcoded `"\n"` when comparing file contents — use `splitlines()`
  or set `newline=""` when writing.

### `cz check` rejects a fixup or merge commit on the branch

`poe check-commit` runs `cz --no-raise 3 check --rev-range origin/master..`.
Squash or amend the offending commit so the branch contains only
Conventional-Commit-shaped messages, or rebase to drop it.

### Coverage drop on CodeCov

The `cover` task generates `coverage.xml` consumed by CodeCov. If coverage
drops, add tests for the new code paths before pushing. Inspect
`coverage.xml` locally or re-run `uv run poe cover` and inspect the
terminal report.

## Pre-commit hooks

Hooks are defined in `.pre-commit-config.yaml` and executed via
[`prek`](https://github.com/j178/prek), a `pre-commit`-compatible runner.
Install once:

```bash
uv run poe setup-pre-commit
```

After install, `prek` runs on every `git commit`. `poe ci` invokes
`prek run --all-files` to mirror what CI will do.
