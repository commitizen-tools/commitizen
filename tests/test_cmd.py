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
