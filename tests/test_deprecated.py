import pytest

from commitizen import changelog_formats, defaults


def test_getattr_deprecated_vars():
    # Test each deprecated variable
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert defaults.bump_pattern == defaults.BUMP_PATTERN
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert defaults.bump_map == defaults.BUMP_MAP
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert (
            defaults.bump_map_major_version_zero == defaults.BUMP_MAP_MAJOR_VERSION_ZERO
        )
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert defaults.bump_message == defaults.BUMP_MESSAGE
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert defaults.change_type_order == defaults.CHANGE_TYPE_ORDER
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert defaults.encoding == defaults.ENCODING
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert defaults.name == defaults.DEFAULT_SETTINGS["name"]
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        assert (
            changelog_formats._guess_changelog_format
            == changelog_formats.guess_changelog_format
        )


def test_getattr_non_existent():
    # Test non-existent attribute
    with pytest.raises(AttributeError) as exc_info:
        _ = defaults.non_existent_attribute
    assert "is not an attribute of" in str(exc_info.value)
