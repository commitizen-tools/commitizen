from commitizen import defaults
from commitizen.cz.base import BaseCommitizen

__all__ = ["CustomizeCommitsCz"]


class CustomizeCommitsCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern
    bump_map = defaults.bump_map

    def __init__(self, config: dict):
        super(CustomizeCommitsCz, self).__init__(config)
        self.custom_config = self.config.get("customize")

    def questions(self) -> list:
        return self.custom_config.get("questions")

    def message(self, answers: dict) -> str:
        message_template = self.custom_config.get("message_template")
        return message_template.format(**answers)

    def example(self) -> str:
        return self.custom_config.get("example")

    def schema(self) -> str:
        return self.custom_config.get("schema")

    def info(self) -> str:
        # TODO
        raise NotImplementedError("Not Implemented yet")
