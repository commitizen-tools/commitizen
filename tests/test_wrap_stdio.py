import sys

from commitizen import wrap_stdio, wrap_stdio_linux, wrap_stdio_unix, wrap_stdio_windows


def test_warp_stdio_exists():
    assert hasattr(wrap_stdio_windows, "sys")
    assert hasattr(wrap_stdio_linux, "sys")
    assert hasattr(wrap_stdio_unix, "sys")


if sys.platform == "win32":  # pragma: no cover
    pass
elif sys.platform == "linux":
    from commitizen.wrap_stdio_linux import WrapStdinLinux, WrapStdoutLinux

    def test_wrap_stdin_linux(mocker):

        tmp_stdin = sys.stdin

        mocker.patch("os.open")
        readerwriter_mock = mocker.mock_open(read_data="data")
        mocker.patch("builtins.open", readerwriter_mock, create=True)

        mocker.patch.object(sys.stdin, "fileno", return_value=0)

        wrap_stdio.wrap_stdio()

        assert sys.stdin != tmp_stdin
        assert isinstance(sys.stdin, WrapStdinLinux)
        assert sys.stdin.encoding == "UTF-8"
        assert sys.stdin.read() == "data"

        wrap_stdio.unwrap_stdio()

        assert sys.stdin == tmp_stdin

    def test_wrap_stdout_linux(mocker):

        tmp_stdout = sys.stdout
        tmp_stderr = sys.stderr

        mocker.patch("os.open")
        readerwriter_mock = mocker.mock_open(read_data="data")
        mocker.patch("builtins.open", readerwriter_mock, create=True)

        wrap_stdio.wrap_stdio()

        assert sys.stdout != tmp_stdout
        assert isinstance(sys.stdout, WrapStdoutLinux)
        sys.stdout.write("stdout")
        readerwriter_mock().write.assert_called_with("stdout")

        assert sys.stderr != tmp_stderr
        assert isinstance(sys.stderr, WrapStdoutLinux)
        sys.stdout.write("stderr")
        readerwriter_mock().write.assert_called_with("stderr")

        wrap_stdio.unwrap_stdio()

        assert sys.stdout == tmp_stdout
        assert sys.stderr == tmp_stderr


else:
    pass
