"""Generate the JSON Schema for the commitizen configuration file.

The schema is derived from the ``Settings`` and ``CzSettings`` TypedDicts in
:mod:`commitizen.defaults` plus the runtime defaults in ``DEFAULT_SETTINGS``,
so it cannot drift from the configuration model. The generated document is
committed at ``schemas/commitizen-config.schema.json`` and kept in sync by
``tests/test_json_schema.py``.

Usage::

    python scripts/gen_json_schema.py                # write the schema file
    python scripts/gen_json_schema.py --check        # exit 1 if out of date

The ``$id`` points at the future schemastore.org location (see issue #1565);
the schema describes the contents of the ``commitizen`` section (the
``[tool.commitizen]`` table in ``pyproject.toml`` or the ``commitizen`` key
in ``.cz.json`` / ``.cz.yaml``).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from pathlib import Path
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

from commitizen.defaults import DEFAULT_SETTINGS, Settings

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "commitizen-config.schema.json"
)
SCHEMA_ID = "https://json.schemastore.org/commitizen.json"
META_SCHEMA = "https://json-schema.org/draft/2020-12/schema"

_ARRAY_ORIGINS = (list, Sequence, Iterable)
_OBJECT_ORIGINS = (dict, OrderedDict, MutableMapping)

# TypedDict classes expose these attributes; used instead of
# ``typing.is_typeddict`` (not available on all supported Python versions).
_TYPED_DICT_MARKERS = ("__required_keys__", "__optional_keys__")

# Best-effort human descriptions for the known settings. Keys without an
# entry still get a type-accurate schema fragment; descriptions only improve
# editor UX and may be extended incrementally.
SETTING_DESCRIPTIONS: dict[str, str] = {
    # Settings
    "allow_abort": "Allow aborting the commit prompt with an empty message.",
    "allowed_prefixes": "Commit message prefixes that are exempt from validation.",
    "always_signoff": "Append a Signed-off-by trailer to every commit.",
    "annotated_tag": "Create annotated tags when bumping.",
    "bump_message": "Template for the bump commit message.",
    "change_type_map": "Map commit types to changelog change types.",
    "changelog_file": "Path of the generated changelog file.",
    "changelog_format": "Changelog output format (for example markdown, asciidoc, textile).",
    "changelog_incremental": "Only add new changelog entries since the last release.",
    "changelog_merge_prerelease": "Merge prerelease changelog entries into the latest stable release.",
    "changelog_start_rev": "Git revision from which changelog generation starts.",
    "customize": "Settings for the custom commit rule (cz_customize).",
    "encoding": "Encoding used to read and write configuration files.",
    "extras": "Additional plugin-specific configuration.",
    "gpg_sign": "Sign commits and tags with GPG when bumping.",
    "ignored_tag_formats": "Tag formats ignored when detecting the latest version.",
    "legacy_tag_formats": "Tag formats used only to detect the latest version.",
    "major_version_zero": "Treat breaking changes as minor bumps while on major version 0.",
    "message_length_limit": "Maximum allowed commit message length (0 means no limit).",
    "name": "Name of the commit rule (cz) plugin to use.",
    "post_bump_hooks": "Commands executed after a successful version bump.",
    "pre_bump_hooks": "Commands executed before a version bump.",
    "prerelease_offset": "Offset applied when bumping a prerelease version.",
    "retry_after_failure": "Retry the commit prompt when validation fails.",
    "style": "Questionary style pairs applied to the interactive prompt.",
    "tag_format": "Format of version tags, for example v$version.",
    "template": "Template used to render the commit message.",
    "update_changelog_on_bump": "Update the changelog automatically on bump.",
    "use_shortcuts": "Enable interactive prompt shortcuts.",
    "version": "Current project version.",
    "version_files": "Files (optionally with a :key suffix) updated with the new version on bump.",
    "version_provider": "Version provider (commitizen, pep621, poetry, npm, scm, uv, ...).",
    "version_scheme": "Version scheme (pep440, semver, semver2).",
    "version_type": "Deprecated alias for version_scheme.",
    "breaking_change_exclamation_in_title": "Treat an exclamation mark in the commit title as a breaking change.",
    # CzSettings (customize)
    "bump_pattern": "Regex used to detect bump-worthy commit messages.",
    "bump_map": "Maps commit message patterns to bump levels.",
    "bump_map_major_version_zero": "Bump map used while on major version 0.",
    "change_type_order": "Order of change types in the changelog.",
    "questions": "Prompt questions for the customized commit flow.",
    "example": "Example commit message shown in help.",
    "schema_pattern": "Regex used to validate the commit message structure.",
    "schema": "Commit message template describing the message structure.",
    "info_path": "Path to a markdown file with additional usage information.",
    "info": "Additional usage information shown in help.",
    "message_template": "Template used to render the final commit message.",
    "commit_parser": "Regex used to parse commit messages for changelog generation.",
    "changelog_pattern": "Regex used to identify changelog-relevant commits.",
}


def _as_nullable(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy of *schema* that also permits ``null``.

    Schemas without an explicit ``type`` (for example the empty schema used
    for ``Any``) already accept every value and are returned unchanged.
    """
    if "type" not in schema:
        return dict(schema)
    current = schema["type"]
    types = [current] if isinstance(current, str) else list(current)
    if "null" not in types:
        types.append("null")
    return {**schema, "type": types}


def _typed_dict_to_schema(typed_dict: type[Any]) -> dict[str, Any]:
    """Convert a TypedDict class into an object schema fragment.

    Properties are derived from the type annotations, and ``required`` from
    the ``__required_keys__`` marker (``total=True`` TypedDicts such as
    ``ConfirmQuestion``).

    ``commitizen.defaults`` only imports ``CzQuestion`` under
    ``TYPE_CHECKING`` (the package never needs it at runtime), so the
    forward reference is resolved from :mod:`commitizen.question` and
    injected into the evaluation namespace via ``localns`` (the
    ``ForwardRef`` overrides ``globalns`` with its module's namespace).
    """
    localns: dict[str, Any] = {}
    module_globals = vars(sys.modules[typed_dict.__module__])
    if "CzQuestion" not in module_globals:
        from commitizen.question import CzQuestion

        localns["CzQuestion"] = CzQuestion
    if "pathlib" not in module_globals:
        import pathlib

        localns["pathlib"] = pathlib
    properties = {
        name: _type_to_schema(hint)
        for name, hint in get_type_hints(typed_dict, localns=localns).items()
    }
    schema: dict[str, Any] = {"type": "object", "properties": properties}
    required = sorted(getattr(typed_dict, "__required_keys__", ()))
    if required:
        schema["required"] = required
    return schema


def _type_to_schema(hint: Any) -> dict[str, Any]:
    """Map a Python type annotation to a JSON Schema fragment.

    Handles the primitives used by ``Settings`` and ``CzSettings``: scalars,
    containers (``list``/``Sequence``/``Iterable``, ``dict``/``OrderedDict``),
    fixed-length tuples, ``None``-unions, nested TypedDicts and ``Any``.
    Unknown or generic hints degrade to an empty schema (accept anything).
    """
    if hint is Any:
        return {}
    if hint is bool:
        return {"type": "boolean"}
    if hint is int:
        return {"type": "integer"}
    if hint is str:
        return {"type": "string"}
    if hint is type(None):
        return {"type": "null"}

    origin = get_origin(hint)

    if origin is Literal:
        return {"enum": list(get_args(hint))}

    if origin in (Union, UnionType):
        args = get_args(hint)
        has_null = type(None) in args
        non_null = [arg for arg in args if arg is not type(None)]
        if len(non_null) == 1:
            schema = _type_to_schema(non_null[0])
            return _as_nullable(schema) if has_null else schema
        alternatives = [_type_to_schema(arg) for arg in non_null]
        # Collapse redundant alternatives (e.g. ``str | pathlib.Path``).
        if all(alt == alternatives[0] for alt in alternatives):
            return _as_nullable(alternatives[0]) if has_null else alternatives[0]
        if has_null:
            alternatives = [_as_nullable(alt) for alt in alternatives]
        return {"anyOf": alternatives}

    if origin is tuple:
        items = [_type_to_schema(arg) for arg in get_args(hint)]
        return {
            "type": "array",
            "prefixItems": items,
            "minItems": len(items),
            "maxItems": len(items),
        }

    if origin in _ARRAY_ORIGINS:
        args = get_args(hint)
        item_hint = args[0] if args else Any
        return {"type": "array", "items": _type_to_schema(item_hint)}

    if origin in _OBJECT_ORIGINS:
        args = get_args(hint)
        value_hint = args[1] if len(args) == 2 else Any
        return {"type": "object", "additionalProperties": _type_to_schema(value_hint)}

    if isinstance(hint, type) and all(hasattr(hint, m) for m in _TYPED_DICT_MARKERS):
        return _typed_dict_to_schema(hint)

    if isinstance(hint, type) and issubclass(hint, Path):
        return {"type": "string"}

    return {}


def _apply_defaults(schema: dict[str, Any], defaults: Mapping[str, Any]) -> None:
    """Attach ``default`` values from *defaults* onto matching properties.

    Only keys present in the generated ``properties`` are touched, so a
    future drift between ``DEFAULT_SETTINGS`` and ``Settings`` cannot leak
    unknown keys into the schema.
    """
    for name, value in defaults.items():
        if name in schema["properties"]:
            schema["properties"][name]["default"] = value


def generate_schema() -> dict[str, Any]:
    """Build the JSON Schema document for the commitizen configuration.

    The top-level object mirrors the ``Settings`` TypedDict; the ``customize``
    property embeds the ``CzSettings`` TypedDict. Unknown keys are permitted
    because commitizen stores them (the ``extras`` setting) and plugins may
    extend the settings in the future.
    """
    settings_schema = _typed_dict_to_schema(Settings)
    _apply_defaults(settings_schema, DEFAULT_SETTINGS)
    for name in settings_schema["properties"]:
        description = SETTING_DESCRIPTIONS.get(name)
        if description is not None:
            settings_schema["properties"][name]["description"] = description
    return {
        "$schema": META_SCHEMA,
        "$id": SCHEMA_ID,
        "title": "commitizen",
        "description": (
            "Configuration for commitizen, the conventional commit tool. "
            "Describes the contents of the commitizen section: the "
            "[tool.commitizen] table in pyproject.toml (referenced with a "
            "#:schema comment) or the commitizen key in a .cz.json file "
            "(referenced with a $schema key)."
        ),
        "type": "object",
        "properties": settings_schema["properties"],
        "additionalProperties": True,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point: write the schema file, or verify it is up to date.

    With ``--check`` the script exits with status 1 when the committed schema
    differs from the generated one; used by CI to catch drift.
    """
    parser = argparse.ArgumentParser(
        description="Generate the commitizen configuration JSON Schema."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the schema file is out of date instead of writing it.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SCHEMA_PATH,
        help=f"Schema output path (default: {SCHEMA_PATH}).",
    )
    args = parser.parse_args(argv)

    generated = json.dumps(generate_schema(), indent=2) + "\n"
    output: Path = args.output

    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != generated:
            print(
                f"schema out of date: run 'python scripts/gen_json_schema.py' "
                f"to regenerate {output}",
                file=sys.stderr,
            )
            return 1
        return 0

    output.write_text(generated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
