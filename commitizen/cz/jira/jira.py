import os
from typing import Any, Dict, List

from commitizen.cz.base import BaseCommitizen

__all__ = ["JiraSmartCz"]


class JiraSmartCz(BaseCommitizen):
    def questions(self) -> List[Dict[str, Any]]:
        questions = [
            {
                "type": "input",
                "name": "message",
                "message": "Git commit message (required):\n",
                # 'validate': RequiredValidator,
                "filter": lambda x: x.strip(),
            },
            {
                "type": "input",
                "name": "issues",
                "message": "Jira Issue ID(s) separated by spaces (required):\n",
                # 'validate': RequiredValidator,
                "filter": lambda x: x.strip(),
            },
            {
                "type": "input",
                "name": "workflow",
                "message": "Workflow command (testing, closed, etc.) (optional):\n",
                "filter": lambda x: "#" + x.strip().replace(" ", "-") if x else "",
            },
            {
                "type": "input",
                "name": "time",
                "message": "Time spent (i.e. 3h 15m) (optional):\n",
                "filter": lambda x: "#time " + x if x else "",
            },
            {
                "type": "input",
                "name": "comment",
                "message": "Jira comment (optional):\n",
                "filter": lambda x: "#comment " + x if x else "",
            },
        ]
        return questions

    def message(self, answers) -> str:
        return " ".join(
            filter(
                bool,
                [
                    answers["message"],
                    answers["issues"],
                    answers["workflow"],
                    answers["time"],
                    answers["comment"],
                ],
            )
        )

    def example(self) -> str:
        return (
            "JRA-34 #comment corrected indent issue\n"
            "JRA-35 #time 1w 2d 4h 30m Total work logged\n"
            "JRA-123 JRA-234 JRA-345 #resolve\n"
            "JRA-123 JRA-234 JRA-345 #resolve #time 2d 5h #comment Task completed "
            "ahead of schedule"
        )

    def schema(self) -> str:
        return "<ignored text> <ISSUE_KEY> <ignored text> #<COMMAND> <optional COMMAND_ARGUMENTS>"  # noqa

    def schema_pattern(self) -> str:
        return r".*[A-Z]{2,}\-[0-9]+( #| .* #).+( #.+)*"

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "jira_info.txt")
        with open(filepath, "r") as f:
            content = f.read()
        return content
