# Playbook: Add or Modify a CLI Flag

Commitizen's CLI is built declaratively with [decli](https://github.com/woile/decli)
and `argparse` in `commitizen/cli.py`. Flags are dicts inside a `data["subcommands"]`
list. End-user documentation: [Commands](../../../commands/init.md).

## Trigger

- "Add a `--<name>` flag to `cz <subcommand>`."
- "Make `--<name>` configurable via the config file."
- "Change the default of `--<flag>`."

## Read first

- `commitizen/cli.py` — the entire CLI schema. Search for the subcommand
  name in the `subcommands` block to find where its `arguments` list
  lives.
- `commitizen/commands/<subcommand>.py` — the command class that receives
  the parsed arguments via `self.arguments`.
- `commitizen/defaults.py:Settings` — TypedDict of all settings; required
  if your flag should also be config-file-readable.
- `tests/test_cli.py` and `tests/test_cli/` — flag-parsing tests.
- `tests/commands/test_<subcommand>_command.py` — behavior tests.
- `docs/commands/<subcommand>.md` — user-facing reference for the
  subcommand.
- `scripts/gen_cli_help_screenshots.py` — regenerates `--help` SVGs.

## Steps

1. **Add the flag** in `commitizen/cli.py` inside the relevant subcommand's
   `arguments` list. Follow the existing dict shape:

   ```python
   {
       "name": ["--my-flag", "-m"],  # or just "--my-flag" if no short
       "action": "store_true",  # or "store", "store_false", ParseKwargs, ...
       "default": False,  # only when not store_true
       "help": "<one-line description, period at end>",
   }
   ```

   Look at neighboring flags in the same subcommand to match style
   (option grouping, help-text tone).
2. **Consume the flag** in `commitizen/commands/<subcommand>.py`. It will
   arrive as `self.arguments["my_flag"]` (dashes become underscores).
3. **Config-file support (optional)**. If the flag should also be settable
   in the user's config file:
    - Add the key to `commitizen/defaults.py:Settings` (and to
      `DEFAULT_SETTINGS` if there is a non-`None` default).
    - In the command, fall back to `self.config.settings["my_flag"]` when
      the CLI value is `None`.
    - Document the setting in the relevant `docs/config/<area>.md` page.
4. **Add tests**:
    - CLI parsing: extend `tests/test_cli/` or `tests/test_cli.py` with a
      case that invokes `cz <subcommand> --my-flag` and asserts the
      parsed namespace.
    - Behavior: extend `tests/commands/test_<subcommand>_command.py`.
5. **Update user docs** at `docs/commands/<subcommand>.md`. If the flag
   has a corresponding config setting, also update
   `docs/config/<area>.md`.
6. **Regenerate the help SVGs** so the new flag appears in the rendered
   docs. See the [update-snapshots playbook](update-snapshots.md) for the
   `poe doc:screenshots` workflow.

## Validate

```bash
uv run pytest tests/test_cli/ tests/test_cli.py tests/commands/test_<subcommand>_command.py -n auto
uv run poe lint
uv run poe doc:build
uv run poe all            # final pre-push
```

## Pitfalls

- **Underscores vs dashes** — argparse converts `--my-flag` to
  `my_flag` in the namespace, but `decli` accepts both. Be consistent
  with neighboring flags.
- **`store_true` with explicit `default`** — argparse uses `False` as the
  implicit default for `store_true`; do not set `default` unless you
  need `None` to detect "user did not pass the flag" (which matters for
  config-file fallback).
- **Mutually exclusive flags** — argparse does not enforce mutual
  exclusion through the `decli` dict schema; validate in the command
  class and raise `commitizen.exceptions.InvalidCommandArgumentError`
  with a clear message.
- **Forgetting the `Settings` TypedDict** when adding a config-file key
  — `read_cfg` will accept the value but `mypy` will flag every read of
  `self.config.settings["my_flag"]`.
- **Breaking flag removals** — see the
  [deprecate-public-api playbook](deprecate-public-api.md). A flag is
  user-facing surface; do not remove it without a deprecation window.
- **Stale `--help` screenshots** — CI does not regenerate them. Run
  `uv run poe doc:screenshots` after any flag change and commit the
  result.

## Stop and ask if

- The flag would change the **exit code** of an existing success path —
  that breaks scripts that depend on exit codes. See
  [Exit Codes](../../../exit_codes.md).
- The flag's behavior overlaps with an existing flag with subtly
  different semantics — propose a deprecation plan first.
- The flag controls something that is currently determined by config
  precedence rules (CLI > env > config); make the precedence explicit
  in the issue.
