import pytest

from commitizen import cmd
from commitizen.exceptions import CharacterSetDecodeError


# https://docs.python.org/3/howto/unicode.html
@pytest.mark.parametrize(
    "s",
    [
        "",
        "ascii",
        "🤦🏻‍♂️",
        "﷽",
        "\u0000",
    ],
)
def test_valid_utf8_encoded_strings(s: str):
    assert s == cmd._try_decode(s.encode("utf-8"))


# A word of caution: just because an encoding can be guessed for a given
# sequence of bytes and because that guessed encoding may yield a decoded
# string, does not mean that that string was the original! For more, see:
# https://docs.python.org/3/library/codecs.html#standard-encodings


@pytest.mark.parametrize(
    "s",
    [
        "",
        "ascii",
        "äöüß",
        "ça va",
        "jak se máte",
    ],
)
def test_valid_cp1250_encoded_strings(s: str):
    """Pick a random, non-utf8 encoding to test."""
    # We just want to make sure it doesn't raise an exception
    cmd._try_decode(s.encode("cp1250"))


def test_invalid_bytes():
    with pytest.raises(CharacterSetDecodeError):
        cmd._try_decode(b"\x73\xe2\x9d\xff\x00")


def test_always_fail_decode():
    class _bytes(bytes):
        def decode(self, encoding="utf-8", errors="strict"):
            raise UnicodeDecodeError(
                encoding, self, 0, 0, "Failing intentionally for testing"
            )

    with pytest.raises(CharacterSetDecodeError):
        cmd._try_decode(_bytes())


def test_run_returns_command_with_shell_false():
    """Test that cmd.run executes a list-based command without shell."""
    c = cmd.run(["python", "-c", "print('hello')"])
    assert c.return_code == 0
    assert "hello" in c.out


def test_run_shell_returns_command_with_shell_true():
    """Test that cmd.run_shell executes a string command via the shell."""
    c = cmd.run_shell("python -c \"print('hello')\"")
    assert c.return_code == 0
    assert "hello" in c.out


def test_run_with_env():
    """Test that cmd.run passes extra environment variables."""
    c = cmd.run(
        ["python", "-c", "import os; print(os.environ['CZ_TEST_VAR'])"],
        env={"CZ_TEST_VAR": "test_value"},
    )
    assert c.return_code == 0
    assert "test_value" in c.out


def test_run_with_string_emits_deprecation_warning():
    """Test that passing a string to cmd.run() emits a DeprecationWarning."""
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        c = cmd.run("python -c \"print('deprecated')\"")
        assert c.return_code == 0
        assert "deprecated" in c.out
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "cmd.run()" in str(w[0].message)
