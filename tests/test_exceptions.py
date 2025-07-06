import pytest

from commitizen.exceptions import ExitCode


def test_from_str_with_decimal():
    """Test from_str with decimal values."""
    assert ExitCode.from_str("0") == ExitCode.EXPECTED_EXIT
    assert ExitCode.from_str("1") == ExitCode.NO_COMMITIZEN_FOUND
    assert ExitCode.from_str("32") == ExitCode.COMMIT_MESSAGE_LENGTH_LIMIT_EXCEEDED


def test_from_str_with_enum_name():
    """Test from_str with enum names."""
    assert ExitCode.from_str("EXPECTED_EXIT") == ExitCode.EXPECTED_EXIT
    assert ExitCode.from_str("NO_COMMITIZEN_FOUND") == ExitCode.NO_COMMITIZEN_FOUND
    assert (
        ExitCode.from_str("COMMIT_MESSAGE_LENGTH_LIMIT_EXCEEDED")
        == ExitCode.COMMIT_MESSAGE_LENGTH_LIMIT_EXCEEDED
    )


def test_from_str_with_whitespace():
    """Test from_str with whitespace in enum names."""
    assert ExitCode.from_str("  EXPECTED_EXIT  ") == ExitCode.EXPECTED_EXIT
    assert ExitCode.from_str("\tNO_COMMITIZEN_FOUND\t") == ExitCode.NO_COMMITIZEN_FOUND


def test_from_str_with_invalid_values():
    """Test from_str with invalid values."""
    with pytest.raises(KeyError):
        ExitCode.from_str("invalid_name")
    with pytest.raises(ValueError):
        ExitCode.from_str("999")  # Out of range decimal
    with pytest.raises(KeyError):
        ExitCode.from_str("")
    with pytest.raises(KeyError):
        ExitCode.from_str(" ")
