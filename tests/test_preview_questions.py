from __future__ import annotations

from typing import TYPE_CHECKING, Any

from commitizen.cz.base import BaseCommitizen
from commitizen.preview_questions import build_preview_questions

if TYPE_CHECKING:
    from collections.abc import Mapping

    import pytest
    from pytest_mock import MockerFixture

    from commitizen.question import CzQuestion


class PreviewCz(BaseCommitizen):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.calls: list[dict[str, Any]] = []

    def questions(self) -> list[CzQuestion]:
        return []

    def message(self, answers: Mapping[str, Any]) -> str:
        self.calls.append(dict(answers))
        return f"{answers.get('prefix', '')}: {answers.get('subject', '')}".strip()

    def schema(self) -> str:
        return ""

    def schema_pattern(self) -> str:
        return ""

    def example(self) -> str:
        return ""

    def info(self) -> str:
        return ""


def _make_fake_prompt_app(mocker: MockerFixture, buffer_text: str):
    """Object graph for get_app().layout.current_buffer.text (prompt_toolkit)."""
    app = mocker.Mock()
    app.layout.current_buffer.text = buffer_text
    return app


def test_build_preview_questions_disabled_returns_original_list(config):
    cz = PreviewCz(config)
    questions: list[CzQuestion] = [
        {"type": "input", "name": "subject", "message": "Subject"},
    ]

    out = build_preview_questions(cz, questions, enabled=False, max_length=50)
    assert out is questions


def test_build_preview_questions_wraps_filter_and_updates_answers_state(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    config,
):
    cz = PreviewCz(config)

    def original_filter(raw: str) -> str:
        return raw.strip().upper()

    questions: list[CzQuestion] = [
        {
            "type": "input",
            "name": "subject",
            "message": "Subject",
            "filter": original_filter,
        }
    ]

    enhanced = build_preview_questions(cz, questions, enabled=True, max_length=50)
    q = enhanced[0]
    assert q["filter"] is not original_filter
    assert q["filter"]("  hello ") == "HELLO"

    monkeypatch.setattr(
        "commitizen.preview_questions.get_app",
        lambda: _make_fake_prompt_app(mocker, "  hello "),
    )
    toolbar_text = q["bottom_toolbar"]()
    assert "HELLO" in toolbar_text
    assert cz.calls, "cz.message should be called by toolbar rendering"
    assert cz.calls[-1]["subject"] == "HELLO"


def test_build_preview_questions_adds_toolbar_only_for_supported_types(config):
    cz = PreviewCz(config)
    questions: list[CzQuestion] = [
        {"type": "input", "name": "a", "message": "A"},
        {"type": "confirm", "name": "b", "message": "B"},
        {"type": "list", "name": "c", "message": "C", "choices": []},
    ]
    enhanced = build_preview_questions(cz, questions, enabled=True, max_length=50)

    assert callable(enhanced[0].get("bottom_toolbar"))
    assert callable(enhanced[1].get("bottom_toolbar"))
    assert "bottom_toolbar" not in enhanced[2]


def test_build_preview_questions_adds_validate_only_for_supported_types(config):
    cz = PreviewCz(config)
    questions: list[CzQuestion] = [
        {"type": "input", "name": "a", "message": "A"},
        {"type": "confirm", "name": "b", "message": "B"},
        {"type": "list", "name": "c", "message": "C", "choices": []},
    ]
    enhanced = build_preview_questions(cz, questions, enabled=True, max_length=3)

    assert callable(enhanced[0].get("validate"))
    assert "validate" not in enhanced[1]
    assert "validate" not in enhanced[2]


def test_toolbar_uses_current_buffer_text_and_subject_builder(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    config,
):
    cz = PreviewCz(config)

    monkeypatch.setattr(
        "commitizen.preview_questions.get_app",
        lambda: _make_fake_prompt_app(mocker, "buffered"),
    )

    questions: list[CzQuestion] = [
        {"type": "input", "name": "subject", "message": "Subject"},
    ]
    enhanced = build_preview_questions(cz, questions, enabled=True, max_length=50)
    toolbar_text = enhanced[0]["bottom_toolbar"]()

    assert "buffered" in toolbar_text


def test_get_current_buffer_text_on_get_app_exception_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
    config,
):
    cz = PreviewCz(config)
    monkeypatch.setattr("commitizen.preview_questions.get_app", lambda: 1 / 0)

    questions: list[CzQuestion] = [
        {"type": "input", "name": "subject", "message": "Subject"},
    ]
    enhanced = build_preview_questions(cz, questions, enabled=True, max_length=50)
    toolbar_text = enhanced[0]["bottom_toolbar"]()

    # With empty buffer text, subject becomes empty -> toolbar still contains counter line
    assert toolbar_text.splitlines()[-1].strip().endswith("chars")


def test_subject_builder_applies_field_filter_and_handles_filter_exception(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    config,
):
    cz = PreviewCz(config)

    def ok_filter(raw: str) -> str:
        return raw.strip()

    def boom_filter(_raw: str) -> str:
        raise RuntimeError("boom")

    questions: list[CzQuestion] = [
        {"type": "input", "name": "subject", "message": "Subject", "filter": ok_filter},
        {"type": "input", "name": "scope", "message": "Scope", "filter": boom_filter},
    ]
    enhanced = build_preview_questions(cz, questions, enabled=True, max_length=50)

    # Update state for 'subject' (ok filter)
    enhanced[0]["filter"]("  hi ")
    # When rendering toolbar for current field 'scope', subject_builder will apply the
    # field filter to the current buffer text; filter exceptions must fallback to raw.
    monkeypatch.setattr(
        "commitizen.preview_questions.get_app",
        lambda: _make_fake_prompt_app(mocker, " SCOPE "),
    )

    # Render toolbar for scope and ensure it still includes subject, and scope raw is used
    toolbar_text = enhanced[1]["bottom_toolbar"]()
    assert "hi" in toolbar_text
    assert cz.calls[-1]["scope"] == " SCOPE "


def test_subject_builder_handles_cz_message_exception_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
    config,
    mocker: MockerFixture,
):
    class BoomCz(PreviewCz):
        def message(self, _answers: Mapping[str, Any]) -> str:
            raise RuntimeError("boom")

    cz = BoomCz(config)

    questions: list[CzQuestion] = [
        {"type": "input", "name": "subject", "message": "Subject"},
    ]
    enhanced = build_preview_questions(cz, questions, enabled=True, max_length=50)

    monkeypatch.setattr(
        "commitizen.interactive_preview.get_terminal_size",
        lambda: mocker.Mock(columns=80),
    )
    toolbar_text = enhanced[0]["bottom_toolbar"]()
    assert toolbar_text.splitlines()[0] == ""
