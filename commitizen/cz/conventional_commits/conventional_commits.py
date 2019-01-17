import os
from commitizen.cz.base import BaseCommitizen

__all__ = ["ConventionalCommitsCz"]


class NoSubjectException(Exception):
    ...


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

    if not text:
        raise NoSubjectException

    return text


class ConventionalCommitsCz(BaseCommitizen):
    def questions(self):
        questions = [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "fix",
                        "name": "fix: A bug fix. Correlates with PATCH in SemVer",
                    },
                    {
                        "value": "feat",
                        "name": "feat: A new feature. Correlates with MINOR in SemVer",
                    },
                    {
                        "value": "BREAKING CHANGE",
                        "name": (
                            "BREAKING CHANGE: introduces a breaking API change. "
                            "Correlates with MAJOR in SemVer"
                        ),
                    },
                    {"value": "docs", "name": "docs: Documentation only changes"},
                    {
                        "value": "style",
                        "name": (
                            "style: Changes that do not affect the "
                            "meaning of the code (white-space, formatting,"
                            " missing semi-colons, etc)"
                        ),
                    },
                    {
                        "value": "refactor",
                        "name": (
                            "refactor: A code change that neither fixes "
                            "a bug nor adds a feature"
                        ),
                    },
                    {
                        "value": "perf",
                        "name": "perf: A code change that improves performance",
                    },
                    {
                        "value": "test",
                        "name": (
                            "test: Adding missing or correcting " "existing tests"
                        ),
                    },
                    {
                        "value": "build",
                        "name": (
                            "build: Changes that affect the build system or "
                            "external dependencies (example scopes: pip, docker, npm)"
                        ),
                    },
                    {
                        "value": "ci",
                        "name": (
                            "ci: Changes to our CI configuration files and "
                            "scripts (example scopes: GitLabCI)"
                        ),
                    },
                ],
            },
            {
                "type": "input",
                "name": "scope",
                "message": (
                    "Scope. Could be anything specifying place of the "
                    "commit change (users, db, poll):\n"
                ),
                "filter": parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
                "message": (
                    "Subject. Concise description of the changes. "
                    "Imperative, lower case and no final dot:\n"
                ),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Body. Motivation for the change and contrast this "
                    "with previous behavior:\n"
                ),
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes:\n"
                ),
            },
        ]
        return questions

    def message(self, answers):
        prefix = answers["prefix"]
        scope = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        message = ""

        if prefix:
            message += "{0}".format(prefix)
            if scope:
                message += "({0})".format(scope)
            message += ": "
        if subject:
            message += "{0}".format(subject)
        if body:
            message += "\n\n{0}".format(body)
        if footer:
            message += "\n\n{0}".format(footer)
        return message

    def example(self):
        return (
            "feat($injector): ability to load new modules after bootstrapping\n"
            "\nThe new method `$injector.loadNewModules(modules)` will add "
            "each of the\ninjectables to the injector and execute all of the "
            "config and run blocks\nfor each module passed to the method.\n"
            "\nCloses #324"
        )

    def schema(self):
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "<footer>"
        )

    def info(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_info.txt")
        with open(filepath, "r") as f:
            content = f.read()
        return content
