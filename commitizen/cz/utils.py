import os
import re
import tempfile

import questionary

from commitizen import git
from commitizen.cz import exceptions

_RE_LOCAL_VERSION = re.compile(r"\+.+")


def required_validator(answer: str, msg: object = None) -> str:
    if not answer:
        raise exceptions.AnswerRequiredError(msg)
    return answer


def multiple_line_breaker(answer: str, sep: str = "|") -> str:
    return "\n".join(line.strip() for line in answer.split(sep) if line)


def get_input_with_continuation(message: str) -> str:
    """Get input with shell-like backslash line continuation."""
    lines = []
    prompt_msg = message + "\n"

    while True:
        try:
            line = questionary.text(prompt_msg).ask()
            if line is None:
                return ""

            if line.rstrip().endswith("\\"):
                lines.append(line.rstrip()[:-1].rstrip())
                prompt_msg = ">"
            else:
                lines.append(line)
                break

        except KeyboardInterrupt:
            return ""

    return "\n".join(lines)


def strip_local_version(version: str) -> str:
    return _RE_LOCAL_VERSION.sub("", version)


def get_backup_file_path() -> str:
    project_root = git.find_git_project_root()
    project = project_root.as_posix().replace("/", "%") if project_root else ""

    user = os.environ.get("USER", "")

    return os.path.join(tempfile.gettempdir(), f"cz.commit%{user}%{project}.backup")
