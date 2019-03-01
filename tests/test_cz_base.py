import pytest

from commitizen.cz.base import BaseCommitizen


class DummyCz(BaseCommitizen):
    def questions(self):
        return [{"type": "input", "name": "commit", "message": "Initial commit:\n"}]

    def message(self, answers):
        return answers["commit"]


def test_base_raises_error():
    with pytest.raises(TypeError):
        BaseCommitizen()


def test_questions():
    cz = DummyCz()
    assert isinstance(cz.questions(), list)


def test_message():
    cz = DummyCz()
    assert cz.message({"commit": "holis"}) == "holis"


def test_example():
    cz = DummyCz()
    with pytest.raises(NotImplementedError):
        cz.example()


def test_schema():
    cz = DummyCz()
    with pytest.raises(NotImplementedError):
        cz.schema()


def test_info():
    cz = DummyCz()
    with pytest.raises(NotImplementedError):
        cz.info()


def test_show_example():
    cz = DummyCz()
    with pytest.raises(NotImplementedError):
        cz.show_example()


def test_show_schema():
    cz = DummyCz()
    with pytest.raises(NotImplementedError):
        cz.show_schema()


def test_show_info():
    cz = DummyCz()
    with pytest.raises(NotImplementedError):
        cz.show_info()


def test_commit(mocker):
    process_mock = mocker.Mock()
    attrs = {"communicate.return_value": (b"commit done", b"")}
    process_mock.configure_mock(**attrs)

    m = mocker.patch("subprocess.Popen")
    m.return_value = process_mock

    cz = DummyCz()
    c = cz.commit("test: run test")
    assert c.out == "commit done"
