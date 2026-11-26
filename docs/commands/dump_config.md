# dump-config

Output the current commitizen configuration (defaults merged with any project overrides) so you can paste it directly into a configuration file as a starting point.

## Usage

```
cz dump-config [--format {toml,yaml,json}]
```

## Options

| Option | Description |
|---|---|
| `--format`, `-f` | Output format: `toml` (default), `yaml`, or `json` |

## Examples

Dump the current configuration as TOML (default):

```bash
cz dump-config
```

Dump as YAML:

```bash
cz dump-config --format yaml
```

Dump as JSON:

```bash
cz dump-config --format json
```

Use the TOML output as a starting point for `pyproject.toml`:

```bash
cz dump-config >> pyproject.toml
```
