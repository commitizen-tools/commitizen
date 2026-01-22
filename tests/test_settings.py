import pytest

from commitizen.config.settings import ChainSettings
from commitizen.defaults import DEFAULT_SETTINGS, Settings


def test_cz_settings_with_empty_config_file_settings() -> None:
    """Test that empty config file settings returns default settings."""
    cz_settings = ChainSettings({})
    assert cz_settings.load_settings() == DEFAULT_SETTINGS


@pytest.mark.parametrize(
    "config_file_settings,expected_name,expected_changelog",
    [
        pytest.param(
            {"name": "custom_cz", "changelog_file": "CUSTOM_CHANGELOG.md"},
            "custom_cz",
            "CUSTOM_CHANGELOG.md",
            id="multiple_config_settings",
        ),
        pytest.param(
            {"name": "test_cz"},
            "test_cz",
            DEFAULT_SETTINGS["changelog_file"],
            id="partial_config_settings",
        ),
    ],
)
def test_cz_settings_merges_config_file_settings(
    config_file_settings: Settings, expected_name: str, expected_changelog: str
) -> None:
    """Test that config file settings override default settings."""
    cz_settings = ChainSettings(config_file_settings)
    result = cz_settings.load_settings()

    assert result["name"] == expected_name
    assert result["changelog_file"] == expected_changelog
    assert result["tag_format"] == DEFAULT_SETTINGS["tag_format"]


@pytest.mark.parametrize(
    "config_file_settings,cli_settings,expected_name,expected_changelog,expected_tag_format",
    [
        pytest.param(
            {"name": "config_cz", "changelog_file": "CONFIG_CHANGELOG.md"},
            {"name": "cli_cz"},
            "cli_cz",
            "CONFIG_CHANGELOG.md",
            DEFAULT_SETTINGS["tag_format"],
            id="cli_overrides_config_file",
        ),
        pytest.param(
            {},
            {"name": "cli_cz", "changelog_file": "CLI_CHANGELOG.md"},
            "cli_cz",
            "CLI_CHANGELOG.md",
            DEFAULT_SETTINGS["tag_format"],
            id="cli_overrides_defaults",
        ),
        pytest.param(
            {
                "name": "config_cz",
                "changelog_file": "CONFIG_CHANGELOG.md",
                "tag_format": "v$version",
            },
            {"name": "cli_cz", "changelog_file": "CLI_CHANGELOG.md"},
            "cli_cz",
            "CLI_CHANGELOG.md",
            "v$version",
            id="cli_overrides_multiple_config_settings",
        ),
        pytest.param(
            {"name": "config_cz", "changelog_file": "CONFIG_CHANGELOG.md"},
            {},
            "config_cz",
            "CONFIG_CHANGELOG.md",
            DEFAULT_SETTINGS["tag_format"],
            id="empty_cli_with_config_file",
        ),
    ],
)
def test_cz_settings_cli_precedence(
    config_file_settings: Settings,
    cli_settings: Settings,
    expected_name: str,
    expected_changelog: str,
    expected_tag_format: str,
) -> None:
    """Test that CLI settings take precedence over config file and defaults."""
    cz_settings = ChainSettings(config_file_settings, cli_settings)
    result = cz_settings.load_settings()

    assert result["name"] == expected_name
    assert result["changelog_file"] == expected_changelog
    assert result["tag_format"] == expected_tag_format
