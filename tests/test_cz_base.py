import pytest

from commitizen.cz.base import BaseCommitizen
from commitizen.exceptions import CommitMessageLengthExceededError


class DummyCz(BaseCommitizen):
    def questions(self):
        return [{"type": "input", "name": "commit", "message": "Initial commit:\n"}]

    def message(self, answers: dict, message_length_limit: int = 0):
        message = answers["commit"]
        self._check_message_length_limit(message, message_length_limit)
        return message


def test_base_raises_error(config):
    with pytest.raises(TypeError):
        BaseCommitizen(config)


def test_questions(config):
    cz = DummyCz(config)
    assert isinstance(cz.questions(), list)


def test_message(config):
    cz = DummyCz(config)
    assert cz.message({"commit": "holis"}) == "holis"


def test_example(config):
    cz = DummyCz(config)
    with pytest.raises(NotImplementedError):
        cz.example()


def test_schema(config):
    cz = DummyCz(config)
    with pytest.raises(NotImplementedError):
        cz.schema()


def test_info(config):
    cz = DummyCz(config)
    with pytest.raises(NotImplementedError):
        cz.info()


def test_process_commit(config):
    cz = DummyCz(config)
    message = cz.process_commit("test(test_scope): this is test msg")
    assert message == "test(test_scope): this is test msg"


def test_message_length_limit(config):
    cz = DummyCz(config)
    commit_message = "123456789"
    message_length = len(commit_message)
    assert cz.message({"commit": commit_message}) == commit_message
    assert (
        cz.message({"commit": commit_message}, message_length_limit=message_length)
        == commit_message
    )
    with pytest.raises(CommitMessageLengthExceededError):
        cz.message({"commit": commit_message}, message_length_limit=message_length - 1)
