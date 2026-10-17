from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, get_type_hints

import jsonschema
import pytest

from commitizen.defaults import DEFAULT_SETTINGS, CzSettings, Settings

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gen_json_schema.py"
SCHEMA_PATH = REPO_ROOT / "schemas" / "commitizen-config.schema.json"
WRAPPER_SCHEMA_PATH = REPO_ROOT / "schemas" / "commitizen-wrapper.schema.json"

VALID_CONFIG: dict[str, Any] = {
    "name": "cz_conventional_commits",
    "version": "0.1.0",
    "version_provider": "commitizen",
    "version_scheme": "pep440",
    "version_files": ["src/__version__.py", "pyproject.toml:version"],
    "tag_format": "$version",
    "update_changelog_on_bump": True,
    "changelog_file": "CHANGELOG.md",
    "changelog_incremental": False,
    "gpg_sign": False,
    "annotated_tag": False,
    "major_version_zero": False,
    "prerelease_offset": 0,
    "retry_after_failure": False,
    "allow_abort": False,
    "message_length_limit": 0,
    "allowed_prefixes": ["Merge", "Revert", "fixup!"],
    "breaking_change_exclamation_in_title": False,
    "use_shortcuts": False,
    "pre_bump_hooks": ["scripts/pre_bump.sh"],
    "post_bump_hooks": [],
    "encoding": "utf-8",
    "style": [["qmark", "fg:#ff9d00 bold"], ["question", "bold"]],
    "customize": {
        "bump_map": {"^feat": "MINOR", "^fix": "PATCH"},
        "bump_pattern": r"^(\w+)(\(.+\))?!?:",
        "message_template": "${{title}}",
        "questions": [
            {"type": "input", "name": "title", "message": "Title"},
            {
                "type": "confirm",
                "name": "is_breaking",
                "message": "Breaking?",
                "default": False,
            },
        ],
    },
    "extras": {"my_plugin": {"custom_key": "value"}},
}


@pytest.fixture(scope="module")
def gen_module() -> Any:
    """Import the generator script without making ``scripts`` a package."""
    spec = importlib.util.spec_from_file_location("gen_json_schema", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_generated_schema_matches_committed_file(gen_module: Any) -> None:
    """The committed schema must be regenerated whenever the models change."""
    expected = SCHEMA_PATH.read_text(encoding="utf-8")
    actual = json.dumps(gen_module.generate_schema(), indent=2) + "\n"

    assert actual == expected


def test_check_flag_passes_on_committed_schema() -> None:
    """The standalone script agrees the committed schema is up to date."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--check"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_check_flag_fails_when_schema_is_missing(
    gen_module: Any, tmp_path: Path
) -> None:
    """A missing or stale schema file is reported as a failure."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--check",
            "--output",
            str(tmp_path / "missing.schema.json"),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )

    assert result.returncode == 1
    assert "out of date" in result.stderr


def test_schema_covers_all_settings_keys(gen_module: Any) -> None:
    """Every Settings key must be present, with no stale extras."""
    properties = gen_module.generate_schema()["properties"]

    assert set(properties) == set(get_type_hints(Settings))


def test_customize_covers_all_cz_settings_keys(gen_module: Any) -> None:
    """The nested customize object mirrors the CzSettings TypedDict."""
    customize = gen_module.generate_schema()["properties"]["customize"]

    assert customize["type"] == "object"
    # Use the gen_module's localns-aware resolution to match what the generator does
    import pathlib

    from commitizen.question import CzQuestion

    localns = {"CzQuestion": CzQuestion, "pathlib": pathlib}
    from typing import get_type_hints as _gth

    expected_keys = set(_gth(CzSettings, localns=localns).keys())
    assert set(customize["properties"]) == expected_keys


def test_no_required_keys(gen_module: Any) -> None:
    """Both TypedDicts are total=False, so no property is required."""
    schema = gen_module.generate_schema()
    customize = schema["properties"]["customize"]

    assert "required" not in schema
    assert "required" not in customize


def test_defaults_are_attached(gen_module: Any) -> None:
    """Runtime defaults from DEFAULT_SETTINGS surface as schema defaults."""
    properties = gen_module.generate_schema()["properties"]

    assert properties["tag_format"]["default"] == DEFAULT_SETTINGS["tag_format"]
    assert (
        properties["version_provider"]["default"]
        == DEFAULT_SETTINGS["version_provider"]
    )
    assert properties["allow_abort"]["default"] is False


def test_type_mapping(gen_module: Any) -> None:
    """Python annotations map to the expected JSON Schema fragments."""
    properties = gen_module.generate_schema()["properties"]
    customize = properties["customize"]["properties"]

    assert properties["allow_abort"]["type"] == "boolean"
    assert properties["message_length_limit"]["type"] == "integer"
    assert properties["version_files"]["type"] == "array"
    assert properties["version_files"]["items"] == {"type": "string"}
    assert customize["bump_map"]["type"] == "object"
    assert customize["bump_map"]["additionalProperties"] == {"type": ["string", "null"]}
    assert customize["bump_map_major_version_zero"]["type"] == "object"
    assert customize["bump_map_major_version_zero"]["additionalProperties"] == {
        "type": ["string", "null"]
    }
    assert properties["style"]["items"]["prefixItems"] == [
        {"type": "string"},
        {"type": "string"},
    ]
    assert properties["style"]["items"]["minItems"] == 2
    assert properties["style"]["items"]["maxItems"] == 2
    assert properties["bump_message"]["type"] == ["string", "null"]
    assert properties["extras"]["type"] == "object"
    assert properties["extras"]["additionalProperties"] == {}


def test_questions_accept_any_question_shape(gen_module: Any) -> None:
    """Question schema supports runtime prompt types and validates required fields."""
    questions = gen_module.generate_schema()["properties"]["customize"]["properties"][
        "questions"
    ]

    assert questions["type"] == "array"
    assert questions["items"]["type"] == "object"
    assert questions["items"]["required"] == ["type", "name", "message"]
    assert questions["items"]["additionalProperties"] is True
    assert questions["items"]["properties"]["choices"]["items"]["anyOf"][0] == {
        "type": "string"
    }


@pytest.mark.parametrize(
    "prompt_type",
    [
        "list",
        "select",
        "input",
        "text",
        "path",
        "editor",
        "checkbox",
        "password",
        "rawselect",
        "autocomplete",
        "confirm",
    ],
)
def test_questions_accept_questionary_prompt_types(
    gen_module: Any, prompt_type: str
) -> None:
    """Runtime questionary prompt types should not be rejected by the schema."""
    question: dict[str, Any] = {
        "type": prompt_type,
        "name": f"{prompt_type}_answer",
        "message": f"Prompt for {prompt_type}",
    }
    if prompt_type in {"list", "select", "checkbox", "rawselect", "autocomplete"}:
        question["choices"] = [
            "feature",
            {"value": "fix", "name": "Fix", "key": "f"},
        ]

    instance = {
        **VALID_CONFIG,
        "customize": {
            **VALID_CONFIG["customize"],
            "questions": [question],
        },
    }
    jsonschema.validate(instance, gen_module.generate_schema())


def test_questions_accept_documented_string_choices_and_optional_confirm_default(
    gen_module: Any,
) -> None:
    """Documented string choices and confirms without an explicit default validate."""
    instance = {
        **VALID_CONFIG,
        "customize": {
            **VALID_CONFIG["customize"],
            "questions": [
                {
                    "type": "select",
                    "name": "change_type",
                    "message": "Select a change type",
                    "choices": ["feature", "fix"],
                },
                {"type": "confirm", "name": "breaking", "message": "Breaking change?"},
            ],
        },
    }

    jsonschema.validate(instance, gen_module.generate_schema())


def test_questions_require_dispatch_fields(gen_module: Any) -> None:
    """A prompt missing a required runtime dispatch field is rejected."""
    instance = {
        **VALID_CONFIG,
        "customize": {
            **VALID_CONFIG["customize"],
            "questions": [{"type": "input", "message": "Missing name"}],
        },
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, gen_module.generate_schema())


def test_wrapper_schema_matches_committed_file(gen_module: Any) -> None:
    """The wrapper schema must be regenerated whenever settings change."""
    expected = WRAPPER_SCHEMA_PATH.read_text(encoding="utf-8")
    actual = json.dumps(gen_module.generate_wrapper_schema(), indent=2) + "\n"

    assert actual == expected


def test_wrapped_json_config_validates(gen_module: Any) -> None:
    """A .cz.json document validates the nested settings, not just the wrapper."""
    wrapped = {"commitizen": VALID_CONFIG}
    jsonschema.validate(wrapped, gen_module.generate_wrapper_schema())

    invalid = {"commitizen": {**VALID_CONFIG, "allow_abort": "yes"}}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid, gen_module.generate_wrapper_schema())


def test_valid_config_validates(gen_module: Any) -> None:
    """A realistic configuration passes validation."""
    jsonschema.validate(VALID_CONFIG, gen_module.generate_schema())


@pytest.mark.parametrize(
    ("overrides", "path"),
    [
        ({"version_files": "CHANGELOG.md"}, "$.version_files"),
        ({"allow_abort": "yes"}, "$.allow_abort"),
        ({"message_length_limit": "0"}, "$.message_length_limit"),
        ({"version": 1.0}, "$.version"),
        ({"style": [["qmark"]]}, "$.style"),
        ({"tag_format": 42}, "$.tag_format"),
        ({"customize": {"bump_map": ["^feat"]}}, "$.customize.bump_map"),
    ],
)
def test_invalid_configs_fail(
    gen_module: Any, overrides: dict[str, Any], path: str
) -> None:
    """Type violations are rejected with a pointer to the offending key."""
    instance = {**VALID_CONFIG, **overrides}

    with pytest.raises(jsonschema.ValidationError) as exc_info:
        jsonschema.validate(instance, gen_module.generate_schema())

    assert exc_info.value.json_path.startswith(path)


def test_unknown_keys_are_permitted(gen_module: Any) -> None:
    """Commitizen stores unknown keys (extras, future plugin settings)."""
    instance = {**VALID_CONFIG, "some_future_plugin_key": {"nested": [1, 2, 3]}}

    jsonschema.validate(instance, gen_module.generate_schema())
