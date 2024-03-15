import re
import os
import tempfile

from commitizen.cz import exceptions
from commitizen import git


def required_validator(answer, msg=None):
    if not answer:
        raise exceptions.AnswerRequiredError(msg)
    return answer


def multiple_line_breaker(answer, sep="|"):
    return "\n".join(line.strip() for line in answer.split(sep) if line)


def strip_local_version(version: str) -> str:
    return re.sub(r"\+.+", "", version)


def get_backup_file_path() -> str:
    return os.path.join(
        tempfile.gettempdir(),
        "cz.commit%{user}%{project_root}.backup".format(
            user=os.environ.get("USER", ""),
            project_root=str(git.find_git_project_root()).replace("/", "%"),
        ),
    )
