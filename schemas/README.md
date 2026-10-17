# JSON Schemas for Commitizen configuration

This directory contains two related schemas because the configuration shapes differ:

- `commitizen-config.schema.json` describes the settings object itself. Use it for the `[tool.commitizen]` table in `pyproject.toml` with a `#:schema` comment.
- `commitizen-wrapper.schema.json` describes a complete `.cz.json` or `.cz.yaml` file, where the settings are nested under the top-level `commitizen` key. The wrapper schema uses the SchemaStore identifier `https://json.schemastore.org/commitizen.json`.

The generator derives settings properties and defaults from Commitizen's configuration types, while its question schema follows the prompt options accepted by the runtime. Run `python scripts/gen_json_schema.py` to regenerate both files, or `python scripts/gen_json_schema.py --check` to verify that both committed schemas are current.

See issue #1565 for the original design discussion.
