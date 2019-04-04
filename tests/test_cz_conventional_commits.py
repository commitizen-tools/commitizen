import pytest
from commitizen import defaults
from commitizen.cz.conventional_commits.conventional_commits import (
    parse_scope,
    parse_subject,
    NoSubjectException,
    ConventionalCommitsCz,
)

config = {"name": defaults.name}

valid_scopes = ["", "simple", "dash-separated", "camelCase" "UPPERCASE"]

scopes_transformations = [["with spaces", "with-spaces"], [None, ""]]

valid_subjects = ["this is a normal text", "aword"]

subjects_transformations = [["with dot.", "with dot"]]

invalid_subjects = ["", "   ", ".", "   .", "", None]


def test_parse_scope_valid_values():
    for valid_scope in valid_scopes:
        assert valid_scope == parse_scope(valid_scope)


def test_scopes_transformations():
    for scopes_transformation in scopes_transformations:
        invalid_scope, transformed_scope = scopes_transformation
        assert transformed_scope == parse_scope(invalid_scope)


def test_parse_subject_valid_values():
    for valid_subject in valid_subjects:
        assert valid_subject == parse_subject(valid_subject)


def test_parse_subject_invalid_values():
    for valid_subject in invalid_subjects:
        with pytest.raises(NoSubjectException):
            parse_subject(valid_subject)


def test_subject_transformations():
    for subject_transformation in subjects_transformations:
        invalid_subject, transformed_subject = subject_transformation
        assert transformed_subject == parse_subject(invalid_subject)


def test_questions():
    conventional_commits = ConventionalCommitsCz(config)
    questions = conventional_commits.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_small_answer():
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "body": "",
        "footer": "",
    }
    message = conventional_commits.message(answers)
    assert message == "fix(users): email pattern corrected"


def test_long_answer():
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "body": "complete content",
        "footer": "closes #24",
    }
    message = conventional_commits.message(answers)
    assert (
        message
        == "fix(users): email pattern corrected\n\ncomplete content\n\ncloses #24"
    )


def test_example():
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    example = conventional_commits.example()
    assert isinstance(example, str)


def test_schema():
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    schema = conventional_commits.schema()
    assert isinstance(schema, str)


def test_info():
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    info = conventional_commits.info()
    assert isinstance(info, str)
