from __future__ import annotations

from collections.abc import Callable
from shutil import get_terminal_size

from prompt_toolkit.utils import get_cwidth

SubjectBuilder = Callable[[str, str], str]


def _wrap_display_width(text: str, width: int) -> list[str]:
    """Wrap text by terminal display width (columns).

    Each character width is computed with get_cwidth so CJK/full-width
    characters are handled correctly.
    """
    if width <= 0 or not text:
        return [text] if text else []

    lines: list[str] = []
    current: list[str] = []
    current_width = 0

    for char in text:
        char_width = get_cwidth(char)
        if current_width + char_width > width and current:
            lines.append("".join(current))
            current = []
            current_width = 0

        current.append(char)
        current_width += char_width

    if current:
        lines.append("".join(current))

    return lines


def make_toolbar_content(
    subject_builder: SubjectBuilder,
    current_field: str,
    current_text: str,
    *,
    max_length: int,
) -> str:
    """Build bottom toolbar content with live preview and length counter.

    - First line (or multiple lines): preview of the commit subject, wrapped by
      terminal display width.
    - Last line: character count, optionally including the max length.
    """
    preview = subject_builder(current_field, current_text)
    current_length = len(preview)

    counter = (
        f"{current_length}/{max_length} chars"
        if max_length > 0
        else f"{current_length} chars"
    )

    try:
        width = get_terminal_size().columns
    except OSError:
        width = 80

    wrapped_preview = _wrap_display_width(preview, width)
    preview_block = "\n".join(wrapped_preview)

    padding = max(0, width - len(counter))
    counter_line = f"{' ' * padding}{counter}"

    return f"{preview_block}\n{counter_line}"


def make_length_validator(
    subject_builder: SubjectBuilder,
    field: str,
    *,
    max_length: int,
) -> Callable[[str], bool | str]:
    """Create a questionary-style validator for subject length.

    The validator:
    - Uses the subject_builder to get the full preview string for the current
      answers_state and field value.
    - Applies max_length on the character count (len). A value of 0 disables
      the limit.
    """

    def _validate(text: str) -> bool | str:
        if max_length <= 0:
            return True

        preview = subject_builder(field, text)
        length = len(preview)
        if length <= max_length:
            return True

        return f"{length}/{max_length} chars (subject length exceeded)"

    return _validate
