from collections.abc import Callable
from typing import Literal, TypedDict


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
    filter: Callable[[str], str]
    bottom_toolbar: Callable[[], str]
    validate: Callable[[str], bool | str]


class InputQuestion(TypedDict, total=False):
    type: Literal["input"]
    name: str
    message: str
    filter: Callable[[str], str]
    bottom_toolbar: Callable[[], str]
    validate: Callable[[str], bool | str]


class ConfirmQuestion(TypedDict, total=False):
    type: Literal["confirm"]
    name: str
    message: str
    default: bool
    filter: Callable[[str], str]
    bottom_toolbar: Callable[[], str]
    validate: Callable[[str], bool | str]


CzQuestion = ListQuestion | InputQuestion | ConfirmQuestion
