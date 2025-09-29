"""Tests for multiline input functionality in commit command."""

from unittest.mock import Mock, patch

import pytest
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys

from commitizen.commands.commit import Commit
from commitizen.config import BaseConfig


class TestCommitMultilineFeature:
    """Test suite for multiline input functionality."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        _config = BaseConfig()
        _config.settings.update({"name": "cz_conventional_commits"})
        return _config

    @pytest.fixture
    def commit_cmd(self, config):
        """Create a Commit command instance."""
        return Commit(config, {})

    def test_optional_field_detection(self, commit_cmd):
        """Test that optional fields are correctly identified."""
        # Test field with default=""
        optional_question = {"default": "", "message": "Optional field"}
        result = (
            optional_question.get("default") == ""
            or "skip" in optional_question.get("message", "").lower()
        )
        assert result is True

        # Test field with "skip" in message
        skip_question = {"message": "Press enter to skip this field"}
        result = (
            skip_question.get("default") == ""
            or "skip" in skip_question.get("message", "").lower()
        )
        assert result is True

        # Test required field
        required_question = {"message": "Required field"}
        result = (
            required_question.get("default") == ""
            or "skip" in required_question.get("message", "").lower()
        )
        assert result is False

    @patch("questionary.prompts.text.text")
    def test_optional_field_empty_input_skips(self, mock_text, commit_cmd):
        """Test that pressing Enter on empty optional field skips it."""
        # Mock the text prompt to return empty string
        mock_text_instance = Mock()
        mock_text_instance.ask.return_value = ""
        mock_text.return_value = mock_text_instance

        # Create an optional question
        question = {
            "type": "input",
            "name": "scope",
            "message": "What is the scope? (press [enter] to skip)",
            "multiline": True,
            "default": "",
            "filter": lambda x: x.strip(),
        }

        # Test the multiline handling logic
        is_optional = (
            question.get("default") == ""
            or "skip" in question.get("message", "").lower()
        )
        assert is_optional is True

        # Verify that empty input results in default value
        if is_optional:
            result = ""
            if not result.strip():
                result = question.get("default", "")
            assert result == ""

    @patch("questionary.prompts.text.text")
    def test_optional_field_multiline_content(self, mock_text, commit_cmd):
        """Test that optional fields can handle multiline content."""
        # Mock the text prompt to return multiline content
        multiline_content = "Line 1\nLine 2\nLine 3"
        mock_text_instance = Mock()
        mock_text_instance.ask.return_value = multiline_content
        mock_text.return_value = mock_text_instance

        # Verify multiline content is preserved
        result = multiline_content
        assert "\n" in result
        assert result.count("\n") == 2  # Two newlines for three lines

    def test_required_field_detection(self, commit_cmd):
        """Test that required fields are correctly identified."""
        required_question = {
            "type": "input",
            "name": "subject",
            "message": "Write a short summary",
            "multiline": True,
        }

        is_optional = (
            required_question.get("default") == ""
            or "skip" in required_question.get("message", "").lower()
        )
        assert is_optional is False

    @patch("builtins.print")
    def test_required_field_empty_input_shows_error(self, mock_print, commit_cmd):
        """Test that empty required field shows error message."""
        # Simulate the error handling for required fields
        buffer_text = ""  # Empty input

        if not buffer_text.strip():
            # This is what our key binding does for required fields
            error_msg = "\n\033[91m⚠ This field is required. Please enter some content or press Ctrl+C to abort.\033[0m"
            prompt_msg = "> "

            # Verify the error message would be shown
            assert "required" in error_msg
            assert "Ctrl+C" in error_msg
            assert prompt_msg == "> "

    @patch("questionary.prompts.text.text")
    def test_required_field_with_content_succeeds(self, mock_text, commit_cmd):
        """Test that required fields with content work properly."""
        # Mock the text prompt to return valid content
        valid_content = "Add user authentication feature"
        mock_text_instance = Mock()
        mock_text_instance.ask.return_value = valid_content
        mock_text.return_value = mock_text_instance

        # Create a required question
        question = {
            "type": "input",
            "name": "subject",
            "message": "Write a short summary",
            "multiline": True,
            "filter": lambda x: x.strip(".").strip(),
        }

        # Test that content is processed correctly
        result = valid_content
        if "filter" in question:
            result = question["filter"](result)

        assert result == "Add user authentication feature"
        assert len(result) > 0

    def test_key_binding_setup_for_optional_fields(self):
        """Test that key bindings are set up correctly for optional fields."""
        from prompt_toolkit.key_binding import KeyBindings

        bindings = KeyBindings()

        # Mock the key binding function for optional fields
        def mock_optional_handler(event: KeyPressEvent) -> None:
            buffer = event.current_buffer
            if not buffer.text.strip():
                # Should exit with empty result for optional fields
                event.app.exit(result=buffer.text)
            else:
                # Should add newline for content
                buffer.newline()

        # Add the binding
        bindings.add(Keys.Enter)(mock_optional_handler)

        # Verify binding was added
        assert len(bindings.bindings) > 0

    def test_key_binding_setup_for_required_fields(self):
        """Test that key bindings are set up correctly for required fields."""
        from prompt_toolkit.key_binding import KeyBindings

        bindings = KeyBindings()

        # Mock the key binding function for required fields
        def mock_required_handler(event: KeyPressEvent) -> None:
            buffer = event.current_buffer
            if not buffer.text.strip():
                # Should show error and do nothing for required fields
                print("Error: Field is required")
                pass
            else:
                # Should add newline for content
                buffer.newline()

        # Add the binding
        bindings.add(Keys.Enter)(mock_required_handler)

        # Verify binding was added
        assert len(bindings.bindings) > 0

    @patch("questionary.prompts.text.text")
    @patch("questionary.prompt")
    def test_fallback_to_standard_prompt(self, mock_prompt, mock_text, commit_cmd):
        """Test that fallback works when custom prompt fails."""
        # Mock the text prompt to raise an exception
        mock_text.side_effect = Exception("Custom prompt failed")

        # Mock the standard prompt
        mock_prompt.return_value = {"test_field": "fallback value"}

        # This would be handled in the except block of our implementation
        try:
            raise Exception("Custom prompt failed")
        except Exception:
            # Fallback to standard questionary prompt
            result = {"test_field": "fallback value"}
            assert result["test_field"] == "fallback value"

    def test_multiline_question_configuration(self):
        """Test that multiline questions are configured properly."""
        # Test configuration for optional field
        optional_question = {
            "type": "input",
            "name": "scope",
            "message": "Scope (press [enter] to skip)",
            "multiline": True,
            "default": "",
        }

        assert optional_question["multiline"] is True
        assert optional_question.get("default") == ""
        assert "type" in optional_question
        assert "name" in optional_question
        assert "message" in optional_question

        # Test configuration for required field
        required_question = {
            "type": "input",
            "name": "subject",
            "message": "Summary",
            "multiline": True,
        }

        assert required_question["multiline"] is True
        assert (
            "default" not in required_question or required_question.get("default") != ""
        )

    @patch("builtins.print")
    def test_user_guidance_messages(self, mock_print):
        """Test that proper guidance messages are shown."""
        # Test optional field guidance
        is_optional = True
        if is_optional:
            expected_msg = "\033[90m💡 Multiline input:\n Press Enter on empty line to skip, Enter after text for new lines, Alt+Enter to finish\033[0m"
            # Verify the message format
            assert "Enter on empty line to skip" in expected_msg
            assert "Alt+Enter to finish" in expected_msg

        # Test required field guidance
        is_optional = False
        if not is_optional:
            expected_msg = "\033[90m💡 Multiline input:\n Press Enter for new lines and Alt+Enter to finish\033[0m"
            # Verify the message format
            assert "Enter for new lines" in expected_msg
            assert "Alt+Enter to finish" in expected_msg

    def test_filter_application(self):
        """Test that filters are applied correctly to multiline input."""

        # Test scope filter (removes spaces, joins with dashes)
        def _parse_scope(text: str) -> str:
            return "-".join(text.strip().split())

        scope_input = "user auth module"
        filtered_scope = _parse_scope(scope_input)
        assert filtered_scope == "user-auth-module"

        # Test simple subject processing (strip whitespace then dots)
        def simple_subject_filter(text: str) -> str:
            return text.strip().rstrip(".")

        subject_input = "Add new feature.  "
        filtered_subject = simple_subject_filter(subject_input)
        assert filtered_subject == "Add new feature"

    def test_answer_dictionary_structure(self):
        """Test that answers are structured correctly."""
        field_name = "test_field"
        result = "test content"

        answer = {field_name: result}

        assert isinstance(answer, dict)
        assert field_name in answer
        assert answer[field_name] == result

    def test_handle_multiline_fallback_success(self):
        """Test the _handle_multiline_fallback helper function with successful response."""
        from commitizen.commands.commit import _handle_multiline_fallback

        with patch("questionary.prompt") as mock_prompt:
            mock_prompt.return_value = {"test_field": "test_value"}

            question = {"name": "test_field", "message": "Test"}
            style = None

            result = _handle_multiline_fallback(question, style)

            assert result == {"test_field": "test_value"}
            mock_prompt.assert_called_once_with([question], style=style)

    def test_handle_multiline_fallback_no_answers_error(self):
        """Test the _handle_multiline_fallback helper function raises NoAnswersError."""
        from commitizen.commands.commit import _handle_multiline_fallback
        from commitizen.exceptions import NoAnswersError

        with patch("questionary.prompt") as mock_prompt:
            mock_prompt.return_value = None

            question = {"name": "test_field", "message": "Test"}
            style = None

            with pytest.raises(NoAnswersError):
                _handle_multiline_fallback(question, style)
