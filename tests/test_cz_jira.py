from commitizen import defaults
from commitizen.cz.jira import JiraSmartCz

config = {"name": defaults.name}


def test_questions():
    cz = JiraSmartCz(config)
    questions = cz.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_answer():
    cz = JiraSmartCz(config)
    answers = {
        "message": "new test",
        "issues": "JRA-34",
        "workflow": "",
        "time": "",
        "comment": "",
    }
    message = cz.message(answers)
    assert message == "new test JRA-34"


def test_example():
    cz = JiraSmartCz(config)
    assert "JRA-34 #comment corrected indent issue\n" in cz.example()


def test_schema():
    cz = JiraSmartCz(config)
    assert "<ignored text>" in cz.schema()


def test_info():
    cz = JiraSmartCz(config)
    assert (
        "Smart Commits allow repository committers to perform "
        "actions such as transitioning JIRA Software"
    ) in cz.info()
