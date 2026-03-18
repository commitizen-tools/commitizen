from __future__ import annotations

from typing import TYPE_CHECKING, Any

from prompt_toolkit.application.current import get_app

from commitizen.interactive_preview import (
    make_length_validator as make_length_validator_preview,
)
from commitizen.interactive_preview import (
    make_toolbar_content as make_toolbar_content_preview,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from commitizen.cz.base import BaseCommitizen
    from commitizen.question import CzQuestion


# Questionary types for interactive preview hooks (length validator / toolbar),
# based on questionary 2.0.1
VALIDATABLE_TYPES = {"input", "text", "password", "path", "checkbox"}
BOTTOM_TOOLBAR_TYPES = {"input", "text", "password", "confirm"}


def build_preview_questions(
    cz: BaseCommitizen,
    questions: list[CzQuestion],
    *,
    enabled: bool,
    max_length: int,
) -> list[CzQuestion]:
    """Return questions enhanced with interactive preview, when enabled."""
    if not enabled:
        return questions

    max_preview_length = max_length

    default_answers: dict[str, Any] = {
        q["name"]: q.get("default", "")
        for q in questions
        if isinstance(q.get("name"), str)
    }
    field_filters: dict[str, Any] = {
        q["name"]: q.get("filter") for q in questions if isinstance(q.get("name"), str)
    }
    answers_state: dict[str, Any] = {}

    def _get_current_buffer_text() -> str:
        try:
            app = get_app()
            buffer = app.layout.current_buffer
            return buffer.text if buffer is not None else ""
        except Exception:
            return ""

    def subject_builder(current_field: str, current_text: str) -> str:
        preview_answers: dict[str, Any] = default_answers.copy()
        preview_answers.update(answers_state)
        if current_field:
            field_filter = field_filters.get(current_field)
            if field_filter:
                try:
                    preview_answers[current_field] = field_filter(current_text)
                except Exception:
                    preview_answers[current_field] = current_text
            else:
                preview_answers[current_field] = current_text
        try:
            return cz.message(preview_answers).partition("\n")[0].strip()
        except Exception:
            return ""

    def make_stateful_filter(
        name: str, original_filter: Callable[[str], str] | None
    ) -> Callable[[str], str]:
        def _filter(raw: str) -> str:
            value = original_filter(raw) if original_filter else raw
            answers_state[name] = value
            return value

        return _filter

    def make_toolbar(name: str) -> Callable[[], str]:
        def _toolbar() -> str:
            return make_toolbar_content_preview(
                subject_builder,
                name,
                _get_current_buffer_text(),
                max_length=max_preview_length,
            )

        return _toolbar

    def make_length_validator(name: str) -> Callable[[str], bool | str]:
        return make_length_validator_preview(
            subject_builder,
            name,
            max_length=max_preview_length,
        )

    enhanced_questions: list[dict[str, object]] = []
    for q in questions:
        q_dict = q.copy()
        q_type = q_dict.get("type")
        name = q_dict.get("name")

        if isinstance(name, str):
            original_filter = q_dict.get("filter")
            q_dict["filter"] = make_stateful_filter(name, original_filter)

            if q_type in BOTTOM_TOOLBAR_TYPES:
                q_dict["bottom_toolbar"] = make_toolbar(name)

            if q_type in VALIDATABLE_TYPES:
                q_dict["validate"] = make_length_validator(name)

        enhanced_questions.append(q_dict)

    return enhanced_questions
