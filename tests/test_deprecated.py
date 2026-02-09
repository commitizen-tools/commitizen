import pytest

from commitizen import changelog_formats, defaults


@pytest.mark.parametrize(
    ("deprecated_var_getter", "replacement"),
    [
        (lambda: defaults.bump_pattern, defaults.BUMP_PATTERN),
        (lambda: defaults.bump_map, defaults.BUMP_MAP),
        (
            lambda: defaults.bump_map_major_version_zero,
            defaults.BUMP_MAP_MAJOR_VERSION_ZERO,
        ),
        (lambda: defaults.bump_message, defaults.BUMP_MESSAGE),
        (lambda: defaults.change_type_order, defaults.CHANGE_TYPE_ORDER),
        (lambda: defaults.encoding, defaults.ENCODING),
        (lambda: defaults.name, defaults.DEFAULT_SETTINGS["name"]),
        (
            lambda: changelog_formats.guess_changelog_format,
            changelog_formats._guess_changelog_format,
        ),
    ],
)
def test_getattr_deprecated_vars(deprecated_var_getter, replacement):
    # Test each deprecated variable
    with pytest.warns(DeprecationWarning, match="is deprecated and will be removed"):
        val = deprecated_var_getter()
    assert val == replacement


def test_getattr_non_existent():
    # Test non-existent attribute
    with pytest.raises(AttributeError, match="is not an attribute of"):
        _ = defaults.non_existent_attribute
