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


class TestRun:
    def test_returns_command_with_shell_false(self):
        """Test that cmd.run executes a list-based command without shell."""
        c = cmd.run(["python", "-c", "print('hello')"])
        assert c.return_code == 0
        assert "hello" in c.out

    def test_with_env(self):
        """Test that cmd.run passes extra environment variables."""
        c = cmd.run(
            ["python", "-c", "import os; print(os.environ['CZ_TEST_VAR'])"],
            env={"CZ_TEST_VAR": "test_value"},
        )
        assert c.return_code == 0
        assert "test_value" in c.out

    def test_with_string_emits_deprecation_warning(self):
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

    def test_stdout_captured(self):
        result = cmd.run(["python", "-c", "print('hello')"])
        assert "hello" in result.out
        assert isinstance(result.stdout, bytes)
        assert b"hello" in result.stdout

    def test_stderr_captured(self):
        result = cmd.run(
            ["python", "-c", "import sys; print('err msg', file=sys.stderr)"]
        )
        assert "err msg" in result.err
        assert isinstance(result.stderr, bytes)
        assert b"err msg" in result.stderr

    def test_zero_return_code_on_success(self):
        result = cmd.run(["python", "-c", "import sys; sys.exit(0)"])
        assert result.return_code == 0

    def test_nonzero_return_code_on_failure(self):
        result = cmd.run(["python", "-c", "import sys; sys.exit(42)"])
        assert result.return_code == 42

    def test_env_passed_to_subprocess(self):
        result = cmd.run(
            ["python", "-c", "import os; print(os.environ['CZ_TEST_VAR'])"],
            env={"CZ_TEST_VAR": "sentinelvalue"},
        )
        assert "sentinelvalue" in result.out
        assert result.return_code == 0

    def test_env_merged_with_os_environ(self, monkeypatch):
        monkeypatch.setenv("CZ_EXISTING_VAR", "fromenv")
        result = cmd.run(
            ["python", "-c", "import os; print(os.environ['CZ_EXISTING_VAR'])"],
            env={"CZ_EXTRA_VAR": "extra"},
        )
        assert "fromenv" in result.out

    def test_empty_stdout_and_stderr(self):
        result = cmd.run(["python", "-c", '"pass"'])
        assert result.out == ""
        assert result.err == ""
        assert result.stdout == b""
        assert result.stderr == b""

    def test_no_env_uses_os_environ(self, monkeypatch):
        monkeypatch.setenv("CZ_NO_ENV_TEST", "inherited")
        result = cmd.run(
            ["python", "-c", "import os; print(os.environ['CZ_NO_ENV_TEST'])"]
        )
        assert "inherited" in result.out


class TestRunShell:
    def test_returns_command_with_shell_true(self):
        """Test that cmd.run_shell executes a string command via the shell."""
        c = cmd.run_shell("python -c \"print('hello')\"")
        assert c.return_code == 0
        assert "hello" in c.out


class TestRunInteractive:
    def test_zero_return_code_on_success(self):
        return_code = cmd.run_interactive(["python", "-c", "import sys; sys.exit(0)"])
        assert return_code == 0

    def test_nonzero_return_code_on_failure(self):
        return_code = cmd.run_interactive(["python", "-c", "import sys; sys.exit(3)"])
        assert return_code == 3

    def test_env_passed_to_subprocess(self):
        return_code = cmd.run_interactive(
            [
                "python",
                "-c",
                "import os, sys; sys.exit(0 if os.environ['CZ_ITEST_VAR'] == 'val' else 1)",
            ],
            env={"CZ_ITEST_VAR": "val"},
        )
        assert return_code == 0

    def test_env_merged_with_os_environ(self, monkeypatch):
        monkeypatch.setenv("CZ_ITEST_EXISTING", "yes")
        return_code = cmd.run_interactive(
            [
                "python",
                "-c",
                "import os, sys; sys.exit(0 if os.environ['CZ_ITEST_EXISTING'] == 'yes' else 1)",
            ],
            env={"CZ_ITEST_EXTRA": "extra"},
        )
        assert return_code == 0

    def test_runs_with_string(self):
        """Test that passing a string to cmd.run_interactive emits a DeprecationWarning."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            return_code = cmd.run_interactive("python -c \"print('hello')\"")
            assert return_code == 0
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "cmd.run_interactive()" in str(w[0].message)


class TestRunInteractiveShell:
    def test_zero_return_code_on_success(self):
        return_code = cmd.run_interactive_shell('python -c "import sys; sys.exit(0)"')
        assert return_code == 0

    def test_nonzero_return_code_on_failure(self):
        return_code = cmd.run_interactive_shell('python -c "import sys; sys.exit(3)"')
        assert return_code == 3

    def test_env_passed_to_subprocess(self):
        return_code = cmd.run_interactive_shell(
            "python -c \"import os, sys; sys.exit(0 if os.environ['CZ_ITEST_VAR'] == 'val' else 1)\"",
            env={"CZ_ITEST_VAR": "val"},
        )
        assert return_code == 0

    def test_env_merged_with_os_environ(self, monkeypatch):
        monkeypatch.setenv("CZ_ITEST_EXISTING", "yes")
        return_code = cmd.run_interactive_shell(
            "python -c \"import os, sys; sys.exit(0 if os.environ['CZ_ITEST_EXISTING'] == 'yes' else 1)\"",
            env={"CZ_ITEST_EXTRA": "extra"},
        )
        assert return_code == 0
