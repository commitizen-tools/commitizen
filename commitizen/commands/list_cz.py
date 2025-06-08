from commitizen import out
from commitizen.config import BaseConfig
from commitizen.cz import registry


class ListCz:
    """List currently installed rules."""

    def __init__(self, config: BaseConfig, *args: object) -> None:
        self.config: BaseConfig = config

    def __call__(self) -> None:
        out.write("\n".join(registry.keys()))
