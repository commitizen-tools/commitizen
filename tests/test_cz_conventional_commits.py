import pytest

from commitizen.cz.conventional_commits.conventional_commits import (
    ConventionalCommitsCz,
    _parse_scope,
    _parse_subject,
)
from commitizen.cz.exceptions import AnswerRequiredError


@pytest.mark.parametrize(
    "valid_scope", ["", "simple", "dash-separated", "camelCaseUPPERCASE"]
)
def test_parse_scope_valid_values(valid_scope):
    assert valid_scope == _parse_scope(valid_scope)


@pytest.mark.parametrize(
    "scopes_transformation", [["with spaces", "with-spaces"], ["", ""]]
)
def test_scopes_transformations(scopes_transformation):
    invalid_scope, transformed_scope = scopes_transformation
    assert transformed_scope == _parse_scope(invalid_scope)


@pytest.mark.parametrize("valid_subject", ["this is a normal text", "aword"])
def test_parse_subject_valid_values(valid_subject):
    assert valid_subject == _parse_subject(valid_subject)


@pytest.mark.parametrize("invalid_subject", ["", "   ", ".", "   .", "\t\t."])
def test_parse_subject_invalid_values(invalid_subject):
    with pytest.raises(AnswerRequiredError):
        _parse_subject(invalid_subject)


@pytest.mark.parametrize("subject_transformation", [["with dot.", "with dot"]])
def test_subject_transformations(subject_transformation):
    invalid_subject, transformed_subject = subject_transformation
    assert transformed_subject == _parse_subject(invalid_subject)


def test_questions(config):
    conventional_commits = ConventionalCommitsCz(config)
    questions = conventional_commits.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_choices_all_have_keyboard_shortcuts(config):
    conventional_commits = ConventionalCommitsCz(config)
    questions = conventional_commits.questions()

    list_questions = (q for q in questions if q["type"] == "list")
    for select in list_questions:
        assert all("key" in choice for choice in select["choices"])


def test_small_answer(config):
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }
    message = conventional_commits.message(answers)
    assert message == "fix(users): email pattern corrected"


def test_long_answer(config):
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "is_breaking_change": False,
        "body": "complete content",
        "footer": "closes #24",
    }
    message = conventional_commits.message(answers)
    assert (
        message
        == "fix(users): email pattern corrected\n\ncomplete content\n\ncloses #24"
    )


def test_breaking_change_in_footer(config):
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "is_breaking_change": True,
        "body": "complete content",
        "footer": "migrate by renaming user to users",
    }
    message = conventional_commits.message(answers)
    print(message)
    assert (
        message
        == "fix(users): email pattern corrected\n\ncomplete content\n\nBREAKING CHANGE: migrate by renaming user to users"
    )


def test_example(config):
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    example = conventional_commits.example()
    assert isinstance(example, str)


def test_schema(config):
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    schema = conventional_commits.schema()
    assert isinstance(schema, str)


def test_info(config):
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    info = conventional_commits.info()
    assert isinstance(info, str)


@pytest.mark.parametrize(
    ("commit_message", "expected_message"),
    [
        (
            "test(test_scope): this is test msg",
            "this is test msg",
        ),
        (
            "test(test_scope)!: this is test msg",
            "this is test msg",
        ),
        (
            "test!(test_scope): this is test msg",
            "",
        ),
    ],
)
def test_process_commit(commit_message, expected_message, config):
    conventional_commits = ConventionalCommitsCz(config)
    message = conventional_commits.process_commit(commit_message)
    assert message == expected_message
