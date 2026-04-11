from __future__ import annotations

from typing import TYPE_CHECKING

from commitizen import interactive_preview

if TYPE_CHECKING:
    import pytest


def test_wrap_display_width_empty_and_non_positive_width():
    assert interactive_preview._wrap_display_width("", 10) == []
    assert interactive_preview._wrap_display_width("abc", 0) == ["abc"]
    assert interactive_preview._wrap_display_width("abc", -1) == ["abc"]


def test_wrap_display_width_ascii_simple_wrap(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(interactive_preview, "get_cwidth", lambda _c: 1)
    assert interactive_preview._wrap_display_width("abcd", 2) == ["ab", "cd"]
    assert interactive_preview._wrap_display_width("abc", 2) == ["ab", "c"]


def test_wrap_display_width_cjk_width_2(monkeypatch: pytest.MonkeyPatch):
    def fake_cwidth(c: str) -> int:
        return 2 if c == "你" else 1

    monkeypatch.setattr(interactive_preview, "get_cwidth", fake_cwidth)
    assert interactive_preview._wrap_display_width("你a", 2) == ["你", "a"]


def test_make_toolbar_content_includes_preview_and_counter_with_max(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
):
    def subject_builder(_field: str, _text: str) -> str:
        return "feat: abc"

    monkeypatch.setattr(
        interactive_preview,
        "get_terminal_size",
        lambda: mocker.Mock(columns=20),
    )

    content = interactive_preview.make_toolbar_content(
        subject_builder, "subject", "abc", max_length=50
    )
    preview, counter = content.splitlines()
    assert preview == "feat: abc"
    assert counter.strip() == "9/50 chars"


def test_make_toolbar_content_counter_without_max_when_zero(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
):
    def subject_builder(_field: str, _text: str) -> str:
        return "fix: a"

    monkeypatch.setattr(
        interactive_preview,
        "get_terminal_size",
        lambda: mocker.Mock(columns=80),
    )
    content = interactive_preview.make_toolbar_content(
        subject_builder, "subject", "a", max_length=0
    )
    assert content.splitlines()[-1].strip() == "6 chars"


def test_make_toolbar_content_terminal_size_oserror_fallback_80(
    monkeypatch: pytest.MonkeyPatch,
):
    def subject_builder(_field: str, _text: str) -> str:
        return "feat: abc"

    def raise_oserror():
        raise OSError("no tty")

    monkeypatch.setattr(interactive_preview, "get_terminal_size", raise_oserror)

    content = interactive_preview.make_toolbar_content(
        subject_builder, "subject", "abc", max_length=50
    )
    assert content.splitlines()[-1].startswith(" " * (80 - len("9/50 chars")))


def test_make_toolbar_content_counter_padding_not_negative(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
):
    def subject_builder(_field: str, _text: str) -> str:
        return "x"

    # Make width tiny so counter is longer than width
    monkeypatch.setattr(
        interactive_preview,
        "get_terminal_size",
        lambda: mocker.Mock(columns=3),
    )
    content = interactive_preview.make_toolbar_content(
        subject_builder, "subject", "x", max_length=50
    )
    assert content.splitlines()[-1] == "1/50 chars"


def test_make_length_validator_disabled_when_max_length_zero():
    def subject_builder(_field: str, text: str) -> str:
        return text

    validate = interactive_preview.make_length_validator(
        subject_builder, "subject", max_length=0
    )
    assert validate("x" * 10) is True


def test_make_length_validator_returns_error_string_when_exceeded():
    def subject_builder(_field: str, text: str) -> str:
        return text

    validate = interactive_preview.make_length_validator(
        subject_builder, "subject", max_length=3
    )
    assert validate("abc") is True
    assert validate("abcd") == "4/3 chars (subject length exceeded)"
