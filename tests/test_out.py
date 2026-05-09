"""Tests for ``commitizen.out``.

Mostly focused on the stdout-encoding helper introduced for #956: the
function must reconfigure non-UTF-8 streams to UTF-8 so commitizen output
(emoji, typographic quotes) doesn't crash with ``UnicodeEncodeError`` on
terminals using locale-dependent encodings such as ``cp1252`` (Windows) or
``ISO8859-1`` (Linux/macOS). The helper also sets ``errors="replace"`` as a
fallback for genuinely un-encodable input such as lone surrogates.
"""

from __future__ import annotations

import io
from typing import Any

from commitizen.out import _ensure_utf8_stdout


class _StubStream(io.TextIOWrapper):
    """Light-weight ``TextIOWrapper`` that records calls to ``reconfigure``.

    Subclassing ``TextIOWrapper`` keeps the ``isinstance`` check in
    ``_ensure_utf8_stdout`` happy without monkey-patching ``sys.stdout``.
    """

    reconfigure_calls: list[dict[str, Any]]
    output: io.BytesIO

    def __init__(self, encoding: str) -> None:
        output = io.BytesIO()
        super().__init__(output, encoding=encoding)
        self.output = output
        self.reconfigure_calls = []

    def reconfigure(self, **kwargs: Any) -> None:
        self.reconfigure_calls.append(kwargs)
        super().reconfigure(**kwargs)


def test_ensure_utf8_stdout_noop_when_already_utf8():
    stream = _StubStream(encoding="utf-8")
    _ensure_utf8_stdout(stream)
    assert stream.reconfigure_calls == []


def test_ensure_utf8_stdout_noop_for_dashless_utf8_alias():
    stream = _StubStream(encoding="UTF8")
    _ensure_utf8_stdout(stream)
    assert stream.reconfigure_calls == []


def test_ensure_utf8_stdout_reconfigures_iso8859_1_terminal():
    """Regression test for #956 (Linux/macOS ``LANG=de_CH.ISO8859-1``)."""
    stream = _StubStream(encoding="latin-1")
    _ensure_utf8_stdout(stream)
    assert stream.reconfigure_calls == [{"encoding": "utf-8", "errors": "replace"}]


def test_ensure_utf8_stdout_reconfigures_windows_cp1252():
    """Regression test for the historical Windows ``cmd.exe`` case."""
    stream = _StubStream(encoding="cp1252")
    _ensure_utf8_stdout(stream)
    assert stream.reconfigure_calls == [{"encoding": "utf-8", "errors": "replace"}]


def test_ensure_utf8_stdout_skips_non_textio_streams():
    class NotATextIO:
        encoding = "latin-1"
        reconfigure_calls: list[dict[str, Any]] = []

        def reconfigure(self, **kwargs: Any) -> None:  # pragma: no cover - unused
            self.reconfigure_calls.append(kwargs)

    stream = NotATextIO()
    _ensure_utf8_stdout(stream)
    assert stream.reconfigure_calls == []


def test_ensure_utf8_stdout_after_reconfigure_can_emit_emoji():
    """End-to-end: after reconfiguration, writing an emoji must not raise."""
    stream = _StubStream(encoding="latin-1")
    _ensure_utf8_stdout(stream)

    # The primary regression guard: switching to UTF-8 means normal Unicode
    # output, such as emoji, no longer raises UnicodeEncodeError.
    stream.write("Configuration complete \U0001f680")
    stream.flush()


def test_ensure_utf8_stdout_replaces_lone_surrogate_on_write():
    """``errors="replace"`` handles genuinely un-encodable input."""
    stream = _StubStream(encoding="latin-1")
    _ensure_utf8_stdout(stream)

    stream.write("ok\udc00ok")
    stream.flush()

    assert stream.output.getvalue() == b"ok?ok"
