import pytest

from commitizen import defaults


def test_getattr_deprecated_vars():
    # Test each deprecated variable
    with pytest.warns(DeprecationWarning) as record:
        assert defaults.bump_pattern == defaults.BUMP_PATTERN
        assert defaults.bump_map == defaults.BUMP_MAP
        assert (
            defaults.bump_map_major_version_zero == defaults.BUMP_MAP_MAJOR_VERSION_ZERO
        )
        assert defaults.bump_message == defaults.BUMP_MESSAGE
        assert defaults.change_type_order == defaults.CHANGE_TYPE_ORDER
        assert defaults.encoding == defaults.ENCODING
        assert defaults.name == defaults.DEFAULT_SETTINGS["name"]

    # Verify warning messages
    assert len(record) == 7
    for warning in record:
        assert "is deprecated and will be removed" in str(warning.message)


def test_getattr_non_existent():
    # Test non-existent attribute
    with pytest.raises(AttributeError) as exc_info:
        _ = defaults.non_existent_attribute
    assert "is not an attribute of" in str(exc_info.value)
