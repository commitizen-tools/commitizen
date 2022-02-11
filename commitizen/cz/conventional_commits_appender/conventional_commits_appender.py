import os
import re

from commitizen import out

from commitizen.config import BaseConfig
from commitizen.cz import ConventionalCommitsCz
from commitizen.cz.utils import required_validator
from commitizen.defaults import Questions

__all__ = ["ConventionalCommitsAppenderCz"]


def parse_scope(text):
    if not text:
        return ""

    scope = text.strip().split()
    if len(scope) == 1:
        return scope[0]

    return "-".join(scope)


def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")


class ConventionalCommitsAppenderCz(ConventionalCommitsCz):
    APPENDER_CZ_LOCAL = "ConventionalCommitsAppenderCz_LOCAL"

    DEFAULT_CONFIG = {
        "prefix": {
            "choices": [
            ]
        },
        "schema_allow_locally": {
            "patterns": [
            ]
        }
    }

    def __init__(self, config: BaseConfig):
        super().__init__(config)
        self.appender_config = dict(config.settings.get(self.__class__.__name__, self.DEFAULT_CONFIG))
        self.q_list = None

        self.questions()

        if self.is_local_run():
            os.environ[self.APPENDER_CZ_LOCAL] = "True"

    def is_local_run(self):
        import os
        return not os.environ.get('CI', False)

    def append_questions(self):
        for element in self.q_list:
            if element["name"] != "prefix":
                continue

            element["choices"].extend(self.appender_config["prefix"]["choices"])

    def questions(self) -> Questions:
        questions: Questions = super().questions()
        self.q_list = questions
        self.append_questions()
        return questions

    def schema_pattern(self, local=False) -> str:
        prefix_choices = [x for x in self.q_list if x["name"] == "prefix"]
        assert len(prefix_choices) == 1
        prefix_choices = prefix_choices[0]["choices"]

        PATTERN = (
            fr"({'|'.join([x['value'] for x in prefix_choices])})"
            r"(\(\S+\))?!?:(\s.*)"
        )

        if local:
            schema_allow_locally = self.appender_config["schema_allow_locally"]["patterns"]
            PATTERN = fr"(^{'|'.join(schema_allow_locally)}|{PATTERN})"

        return PATTERN

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_appender_info.txt")
        content = ''
        with open(filepath, "r") as f:
            content += f.read()
        filepath = os.path.join(dir_path, "..", "conventional_commits", "conventional_commits_info.txt")
        with open(filepath, "r") as f:
            content += f.read()
        return content

    def process_commit(self, commit: str, local=False) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            if os.environ.get('CI', None) and not local:
                return self.process_commit(commit, True)

            return ""

        if os.environ.get('CI', None) and local:
            out.warning("Title line is only allowed locally!\nIt will be rejected upstream.")

        return m.group(3).strip()
