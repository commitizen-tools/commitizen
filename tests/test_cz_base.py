import pytest
from commitizen.cz.base import BaseCommitizen


class DummyCz(BaseCommitizen):
    def questions(self):
        return [{"type": "input", "name": "commit", "message": "Initial commit:\n"}]

    def message(self, answers):
        return answers["commit"]

    def example(self):
        return "example"

    def schema(self):
        return "schema"

    def info(self):
        return "info"


def test_base_raises_error():
    with pytest.raises(TypeError):
        BaseCommitizen()


def test_questions():
    cz = DummyCz()
    assert isinstance(cz.questions(), list)


def test_message():
    cz = DummyCz()
    assert cz.message({"commit": "holis"}) == "holis"
