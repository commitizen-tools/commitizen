from unittest.mock import mock_open, patch

import pytest

from commitizen.cz.conventional_commits.conventional_commits import (
    ConventionalCommitsCz,
    parse_scope,
    parse_subject,
)
from commitizen.cz.conventional_commits.translation_multilanguage import (
    FILENAME,
    MULTILANGUAGE,
    generate_key,
    load_multilanguage,
    save_multilanguage,
    translate_text,
    translate_text_from_eng,
)
from commitizen.cz.exceptions import AnswerRequiredError

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
        with pytest.raises(AnswerRequiredError):
            parse_subject(valid_subject)


def test_subject_transformations():
    for subject_transformation in subjects_transformations:
        invalid_subject, transformed_subject = subject_transformation
        assert transformed_subject == parse_subject(invalid_subject)


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
        == "fix(users): email pattern corrected\n\ncomplete content\n\ncloses #24"  # noqa
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
        == "fix(users): email pattern corrected\n\ncomplete content\n\nBREAKING CHANGE: migrate by renaming user to users"  # noqa
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


def test_load_multilanguage():
    mock_data = "hello_en=hello\nworld_fr=monde\n"

    file = "builtins.open"
    with patch(file, mock_open(read_data=mock_data)):
        MULTILANGUAGE = load_multilanguage(file)

    assert MULTILANGUAGE == {"hello_en": "hello", "world_fr": "monde"}


def test_save_multilanguage():
    key = "hello_fr"
    value = "bonjour"
    with patch("builtins.open", mock_open()) as mocked_file:
        save_multilanguage(key, value)
        mocked_file.assert_called_once_with(FILENAME, "a")
        mocked_file().write.assert_called_once_with(f"{key}={value}\n")


def test_generate_key():
    original_key = "hello"
    to_lang = "fr"
    expected_key = "hello_fr"
    assert generate_key(original_key, to_lang) == expected_key


def test_translate_text_error():
    with patch("translate.Translator") as MockTranslator:
        mock_translator = MockTranslator.return_value
        mock_translator.translate.return_value = "IS AN INVALID TARGET LANGUAGE"

        text = "hello"
        from_lang = "en"
        to_lang = "xx"  # Langue invalid
        translated = translate_text(text, from_lang, to_lang)

        assert translated == text


def test_translate_text_from_eng_default_language():
    text = "hello"
    to_lang = "en"
    key = "hello"

    translated = translate_text_from_eng(text, to_lang, key)

    # La langue de destination est l'anglais, donc le texte doit être renvoyé tel quel
    assert translated == "hello"


def test_translate_text_with_is_translating_false():
    global IS_TRANSLATING
    IS_TRANSLATING = False  # Simuler que la traduction est désactivée

    text = "hello"
    from_lang = "en"
    to_lang = "fr"

    translated = translate_text(text, from_lang, to_lang)

    # IS_TRANSLATING est False, donc le texte doit être retourné sans modification
    assert translated == text


def test_load_multilanguage_empty_file():
    with patch("builtins.open", mock_open(read_data="")):
        load_multilanguage()
    assert MULTILANGUAGE == {}


def test_load_multilanguage_malformed_file():
    malformed_data = "hello=bonjour\ninvalid-line\nworld=monde\n"
    file = "builtins.open"
    with patch(file, mock_open(read_data=malformed_data)):
        MULTILANGUAGE = load_multilanguage(file)

    # Devrait ignorer les lignes malformées
    assert MULTILANGUAGE == {"hello": "bonjour", "world": "monde"}
