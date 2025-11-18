import os
import re
import tempfile
from pathlib import Path

from commitizen import git
from commitizen.cz import exceptions

_RE_LOCAL_VERSION = re.compile(r"\+.+")


def required_validator(answer: str, msg: object = None) -> str:
    if not answer:
        raise exceptions.AnswerRequiredError(msg)
    return answer


def multiple_line_breaker(answer: str, sep: str = "|") -> str:
    return "\n".join(line.strip() for line in answer.split(sep) if line)


def strip_local_version(version: str) -> str:
    return _RE_LOCAL_VERSION.sub("", version)


def get_backup_file_path() -> Path:
    project_root = git.find_git_project_root()
    project = project_root.as_posix().replace("/", "%") if project_root else ""

    user = os.environ.get("USER", "")
    return Path(tempfile.gettempdir(), f"cz.commit%{user}%{project}.backup")
