import os
import re
import tempfile

from commitizen import git
from commitizen.cz import exceptions


def required_validator(answer: str, msg=None) -> str:
    if not answer:
        raise exceptions.AnswerRequiredError(msg)
    return answer


def required_validator_scope(
    answer: str,
    msg: str = "! Error: Scope is required",
) -> str:
    return required_validator(answer, msg)


def required_validator_subject_strip(
    answer: str,
    msg: str = "! Error: Subject is required",
) -> str:
    return required_validator(answer.strip(".").strip(), msg)


def required_validator_title_strip(
    answer: str,
    msg: str = "! Error: Title is required",
) -> str:
    return required_validator(answer.strip(".").strip(), msg)


def multiple_line_breaker(answer: str, sep: str = "|") -> str:
    return "\n".join(line.strip() for line in answer.split(sep) if line)


def strip_local_version(version: str) -> str:
    return re.sub(r"\+.+", "", version)


def get_backup_file_path() -> str:
    project_root = git.find_git_project_root()

    if project_root is None:
        project = ""
    else:
        project = project_root.as_posix().replace("/", "%")

    user = os.environ.get("USER", "")
    return os.path.join(tempfile.gettempdir(), f"cz.commit%{user}%{project}.backup")
