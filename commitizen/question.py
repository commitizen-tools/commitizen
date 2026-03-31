from collections.abc import Callable
from typing import Literal, TypedDict

from prompt_toolkit.key_binding import KeyBindings


class Choice(TypedDict, total=False):
    value: str
    name: str
    key: str


class ListQuestion(TypedDict, total=False):
    type: Literal["list"]
    name: str
    message: str
    choices: list[Choice]
    use_shortcuts: bool


class InputQuestion(TypedDict, total=False):
    type: Literal["input"]
    name: str
    message: str
    filter: Callable[[str], str]
    multiline: bool
    key_bindings: KeyBindings


class ConfirmQuestion(TypedDict):
    type: Literal["confirm"]
    name: str
    message: str
    default: bool


CzQuestion = ListQuestion | InputQuestion | ConfirmQuestion
