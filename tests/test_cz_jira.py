from commitizen.cz.jira import JiraSmartCz


def test_questions(mock_config):
    cz = JiraSmartCz(mock_config)
    questions = cz.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_answer(mock_config):
    cz = JiraSmartCz(mock_config)
    answers = {
        "message": "new test",
        "issues": "JRA-34",
        "workflow": "",
        "time": "",
        "comment": "",
    }
    message = cz.message(answers)
    assert message == "new test JRA-34"


def test_example(mock_config):
    cz = JiraSmartCz(mock_config)
    assert "JRA-34 #comment corrected indent issue\n" in cz.example()


def test_schema(mock_config):
    cz = JiraSmartCz(mock_config)
    assert "<ignored text>" in cz.schema()


def test_info(mock_config):
    cz = JiraSmartCz(mock_config)
    assert (
        "Smart Commits allow repository committers to perform "
        "actions such as transitioning JIRA Software"
    ) in cz.info()
