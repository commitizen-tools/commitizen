from typing import Callable, Literal, TypedDict, Union


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


class ConfirmQuestion(TypedDict):
    type: Literal["confirm"]
    name: str
    message: str
    default: bool


CzQuestion = Union[ListQuestion, InputQuestion, ConfirmQuestion]
