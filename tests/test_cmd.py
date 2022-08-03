import pytest

from commitizen import cmd
from commitizen.exceptions import CharacterSetDecodeError


# https://docs.python.org/3/howto/unicode.html
def test_valid_utf8_encoded_strings():
    valid_strings = (
        "",
        "ascii",
        "🤦🏻‍♂️",
        "﷽",
        "\u0000",
    )
    assert all(s == cmd._try_decode(s.encode("utf-8")) for s in valid_strings)


# A word of caution: just because an encoding can be guessed for a given
# sequence of bytes and because that guessed encoding may yield a decoded
# string, does not mean that that string was the original! For more, see:
# https://docs.python.org/3/library/codecs.html#standard-encodings


# Pick a random, non-utf8 encoding to test.
def test_valid_cp1250_encoded_strings():
    valid_strings = (
        "",
        "ascii",
        "äöüß",
        "ça va",
        "jak se máte",
    )
    for s in valid_strings:
        assert cmd._try_decode(s.encode("cp1250")) or True


def test_invalid_bytes():
    invalid_bytes = (b"\x73\xe2\x9d\xff\x00",)
    for s in invalid_bytes:
        with pytest.raises(CharacterSetDecodeError):
            cmd._try_decode(s)


def test_always_fail_decode():
    class _bytes(bytes):
        def decode(self, encoding="utf-8", errors="strict"):
            raise UnicodeDecodeError(
                encoding, self, 0, 0, "Failing intentionally for testing"
            )

    with pytest.raises(CharacterSetDecodeError):
        cmd._try_decode(_bytes())
