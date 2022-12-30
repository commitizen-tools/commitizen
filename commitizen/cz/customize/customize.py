try:
    from jinja2 import Template
except ImportError:
    from string import Template  # type: ignore

import re
from typing import Optional

from commitizen import defaults
from commitizen.config import BaseConfig
from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions
from commitizen.exceptions import (
    InvalidCommitMessageError,
    MissingCzCustomizeConfigError,
)

__all__ = ["CustomizeCommitsCz", "CustomizeCommitValidationCz"]


class CustomizeCommitsCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern
    bump_map = defaults.bump_map
    change_type_order = defaults.change_type_order

    def __init__(self, config: BaseConfig):
        super(CustomizeCommitsCz, self).__init__(config)

        if "customize" not in self.config.settings:
            raise MissingCzCustomizeConfigError()
        self.custom_settings = self.config.settings["customize"]

        custom_bump_pattern = self.custom_settings.get("bump_pattern")
        if custom_bump_pattern:
            self.bump_pattern = custom_bump_pattern

        custom_bump_map = self.custom_settings.get("bump_map")
        if custom_bump_map:
            self.bump_map = custom_bump_map

        custom_change_type_order = self.custom_settings.get("change_type_order")
        if custom_change_type_order:
            self.change_type_order = custom_change_type_order

        commit_parser = self.custom_settings.get("commit_parser")
        if commit_parser:
            self.commit_parser = commit_parser

        changelog_pattern = self.custom_settings.get("changelog_pattern")
        if changelog_pattern:
            self.changelog_pattern = changelog_pattern

        change_type_map = self.custom_settings.get("change_type_map")
        if change_type_map:
            self.change_type_map = change_type_map

    def questions(self) -> Questions:
        return self.custom_settings.get("questions", [{}])

    def message(self, answers: dict) -> str:
        message_template = Template(self.custom_settings.get("message_template", ""))
        if getattr(Template, "substitute", None):
            return message_template.substitute(**answers)  # type: ignore
        else:
            return message_template.render(**answers)

    def example(self) -> Optional[str]:
        return self.custom_settings.get("example")

    def schema_pattern(self) -> Optional[str]:
        return self.custom_settings.get("schema_pattern")

    def schema(self) -> Optional[str]:
        return self.custom_settings.get("schema")

    def info(self) -> Optional[str]:
        info_path = self.custom_settings.get("info_path")
        info = self.custom_settings.get("info")
        if info_path:
            with open(info_path, "r") as f:
                content = f.read()
            return content
        elif info:
            return info
        return None


class CustomizeCommitValidationCz(CustomizeCommitsCz):
    def validate_commit(self, pattern, commit, allow_abort) -> bool:
        """
        Validates that a commit message doesn't contain certain tokens.
        """
        if not commit.message:
            return allow_abort

        invalid_tokens = ["Merge", "Revert", "Pull request", "fixup!", "squash!"]
        for token in invalid_tokens:
            if commit.message.startswith(token):
                raise InvalidCommitMessageError(
                    f"Commits may not start with the token {token}."
                )

        return re.match(pattern, commit.message)

    def validate_commits(self, commits, allow_abort):
        """
        Validates a list of commits against the configured commit validation schema.
        See the schema() and example() functions for examples.
        """

        pattern = self.schema_pattern()

        displayed_msgs_content = []
        for commit in commits:
            message = ""
            valid = False
            try:
                valid = self.validate_commit(pattern, commit, allow_abort)
            except InvalidCommitMessageError as e:
                message = e.message

            if not valid:
                displayed_msgs_content.append(
                    f"commit {commit.rev}\n"
                    f"Author: {commit.author} <{commit.author_email}>\n\n"
                    f"{commit.message}\n\n"
                    f"commit validation: failed! {message}\n"
                )

        if displayed_msgs_content:
            displayed_msgs = "\n".join(displayed_msgs_content)
            raise InvalidCommitMessageError(
                f"{displayed_msgs}\n"
                "Please enter a commit message in the commitizen format.\n"
            )
