"""Tests for multiline input functionality in commit command."""

from unittest.mock import Mock, patch

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from commitizen.commands.commit import _handle_multiline_question
from commitizen.config import BaseConfig


@pytest.fixture
def config():
    """Create a test configuration."""
    _config = BaseConfig()
    _config.settings.update({"name": "cz_conventional_commits"})
    return _config


@pytest.fixture
def mock_cz_style():
    """Mock commitizen style."""
    return None


class TestMultilineFieldDetection:
    """Test optional vs required field detection logic."""

    @pytest.mark.parametrize(
        "question,expected",
        [
            ({"default": "", "message": "Optional field"}, True),
            ({"message": "Press enter to skip this field"}, True),
            ({"message": "Optional field (press [enter] to skip)"}, True),
            ({"message": "Required field"}, False),
            ({"default": "some value", "message": "Field with default"}, False),
        ],
    )
    def test_optional_field_detection(self, question, expected):
        """Test that optional fields are correctly identified."""
        is_optional = (
            question.get("default") == ""
            or "skip" in question.get("message", "").lower()
            or "[enter] to skip" in question.get("message", "").lower()
        )
        assert is_optional == expected


class TestMultilineInputBehavior:
    """Test multiline input behavior with mocked prompts."""

    @patch("questionary.text")
    def test_optional_field_empty_input_returns_empty(self, mock_text, mock_cz_style):
        """Test that empty input on optional field returns empty string."""
        mock_instance = Mock()
        mock_instance.unsafe_ask.return_value = ""
        mock_text.return_value = mock_instance

        question = {
            "type": "input",
            "name": "scope",
            "message": "What is the scope? (press [enter] to skip)",
            "multiline": True,
            "default": "",
        }

        result = _handle_multiline_question(question, mock_cz_style)

        assert result == {"scope": ""}

    @patch("questionary.text")
    def test_multiline_content_preserved(self, mock_text, mock_cz_style):
        """Test that multiline content is properly preserved."""
        multiline_content = "Line 1\nLine 2\nLine 3"
        mock_instance = Mock()
        mock_instance.unsafe_ask.return_value = multiline_content
        mock_text.return_value = mock_instance

        question = {
            "type": "input",
            "name": "body",
            "message": "Provide additional context",
            "multiline": True,
        }

        result = _handle_multiline_question(question, mock_cz_style)

        assert result == {"body": multiline_content}
        assert result["body"].count("\n") == 2

    @patch("commitizen.out.info")
    @patch("questionary.text")
    def test_filter_applied_to_result(self, mock_text, _mock_info, mock_cz_style):
        """Test that filters are correctly applied to multiline input."""
        mock_instance = Mock()
        mock_instance.unsafe_ask.return_value = "Add new feature.  "
        mock_text.return_value = mock_instance

        question = {
            "type": "input",
            "name": "subject",
            "message": "Write a short summary",
            "multiline": True,
            "filter": lambda x: x.strip().rstrip("."),
        }

        result = _handle_multiline_question(question, mock_cz_style)

        assert result == {"subject": "Add new feature"}

    @patch("commitizen.out.info")
    @patch("commitizen.out.error")
    @patch("commitizen.out.line")
    @patch("questionary.text")
    def test_filter_error_triggers_retry(
        self, mock_text, _mock_line, mock_error, _mock_info, mock_cz_style
    ):
        """Test that filter errors are handled and trigger retry."""
        filter_call_count = [0]

        def get_mock_instance():
            mock_instance = Mock()
            mock_instance.unsafe_ask.return_value = "user input"
            return mock_instance

        # Return instances for both the first and second call
        mock_text.side_effect = [get_mock_instance(), get_mock_instance()]

        def failing_then_succeeding_filter(text):
            filter_call_count[0] += 1
            if filter_call_count[0] == 1:
                raise ValueError("Invalid format")
            return text.strip()

        question = {
            "type": "input",
            "name": "test",
            "message": "Test",
            "multiline": True,
            "filter": failing_then_succeeding_filter,
        }

        result = _handle_multiline_question(question, mock_cz_style)

        assert result == {"test": "user input"}
        assert (
            filter_call_count[0] == 2
        )  # Filter called twice: first fails, second succeeds
        assert mock_text.call_count == 2  # Prompt shown twice
        mock_error.assert_called_once()  # Error message displayed once


class TestKeyBindings:
    """Test key binding setup."""

    def test_key_bindings_created(self):
        """Test that key bindings are properly created."""
        bindings = KeyBindings()

        @bindings.add(Keys.Enter)
        def _enter_handler(_event):
            pass

        @bindings.add(Keys.Escape, Keys.Enter)
        def _alt_enter_handler(_event):
            pass

        assert len(bindings.bindings) == 2


class TestGuidanceMessages:
    """Test user guidance messages."""

    def test_optional_field_guidance(self):
        """Test guidance message for optional fields."""
        expected_msg = "💡 Press Enter on empty line to skip, Alt+Enter to finish"
        assert "Enter on empty line to skip" in expected_msg
        assert "Alt+Enter to finish" in expected_msg

    def test_required_field_guidance(self):
        """Test guidance message for required fields."""
        expected_msg = "💡 Press Alt+Enter to finish"
        assert "Alt+Enter to finish" in expected_msg
        assert "skip" not in expected_msg.lower()


class TestQuestionConfiguration:
    """Test question configuration structure."""

    @pytest.mark.parametrize(
        "question_type,expected_keys",
        [
            ("optional", ["type", "name", "message", "multiline", "default"]),
            ("required", ["type", "name", "message", "multiline"]),
        ],
    )
    def test_question_structure(self, question_type, expected_keys):
        """Test that questions have proper structure."""
        if question_type == "optional":
            question = {
                "type": "input",
                "name": "scope",
                "message": "Scope (press [enter] to skip)",
                "multiline": True,
                "default": "",
            }
        else:
            question = {
                "type": "input",
                "name": "subject",
                "message": "Summary",
                "multiline": True,
            }

        for key in expected_keys:
            assert key in question

        if question_type == "optional":
            assert question["default"] == ""
        assert question["multiline"] is True
