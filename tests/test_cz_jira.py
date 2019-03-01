from commitizen.cz.jira import JiraSmartCz


def test_questions():
    cz = JiraSmartCz()
    questions = cz.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_answer():
    cz = JiraSmartCz()
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
    cz = JiraSmartCz()
    assert "JRA-34 #comment corrected indent issue\n" in cz.example()


def test_schema():
    cz = JiraSmartCz()
    assert "<ignored text>" in cz.schema()


def test_info():
    cz = JiraSmartCz()
    assert (
        "Smart Commits allow repository committers to perform "
        "actions such as transitioning JIRA Software"
    ) in cz.info()
