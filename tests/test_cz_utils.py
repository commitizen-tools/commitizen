import pytest
from pytest_mock import MockFixture

from commitizen.cz import exceptions, utils


def test_multiline_key_bindings_enter_submits_on_empty(mocker: MockFixture):
    kb = utils.get_multiline_key_bindings()
    handler = kb.get_bindings_for_keys(("enter",))[0].handler

    buff = mocker.MagicMock()
    buff.text = ""
    event = mocker.MagicMock()
    event.app.current_buffer = buff

    handler(event)
    buff.validate_and_handle.assert_called_once()
    buff.insert_text.assert_not_called()


def test_multiline_key_bindings_enter_inserts_newline(mocker: MockFixture):
    kb = utils.get_multiline_key_bindings()
    handler = kb.get_bindings_for_keys(("enter",))[0].handler

    buff = mocker.MagicMock()
    buff.text = "some content"
    event = mocker.MagicMock()
    event.app.current_buffer = buff

    handler(event)
    buff.insert_text.assert_called_once_with("\n")
    buff.validate_and_handle.assert_not_called()


def test_required_validator():
    assert utils.required_validator("test") == "test"

    with pytest.raises(exceptions.AnswerRequiredError):
        utils.required_validator("")


def test_multiple_line_breaker():
    message = "this is the first line    | and this is the second line   "
    result = utils.multiple_line_breaker(message)
    assert result == "this is the first line\nand this is the second line"

    result = utils.multiple_line_breaker(message, "is")
    assert result == "th\n\nthe first line    | and th\n\nthe second line"


def test_get_backup_file_path_no_project_root(mocker: MockFixture):
    project_root_mock = mocker.patch("commitizen.git.find_git_project_root")
    project_root_mock.return_value = None
    assert utils.get_backup_file_path()
