from commitizen.cz.jira import JiraSmartCz


def test_questions(default_config):
    cz = JiraSmartCz(default_config)
    questions = cz.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_answer(default_config):
    cz = JiraSmartCz(default_config)
    answers = {
        "message": "new test",
        "issues": "JRA-34",
        "workflow": "",
        "time": "",
        "comment": "",
    }
    message = cz.message(answers)
    assert message == "new test JRA-34"


def test_example(default_config):
    cz = JiraSmartCz(default_config)
    assert "JRA-34 #comment corrected indent issue\n" in cz.example()


def test_schema(default_config):
    cz = JiraSmartCz(default_config)
    assert "<ignored text>" in cz.schema()


def test_info(default_config):
    cz = JiraSmartCz(default_config)
    assert (
        "Smart Commits allow repository committers to perform "
        "actions such as transitioning JIRA Software"
    ) in cz.info()
