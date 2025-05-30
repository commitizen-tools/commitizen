from typing import Callable, Literal, Optional, Union

from pydantic import BaseModel, Field


class CzModel(BaseModel):
    def dict(self, **kwargs):
        return super().dict(**{"exclude_unset": True, **kwargs})


class Choice(CzModel):
    value: str
    name: str
    key: Optional[str] = None


class QuestionBase(CzModel):
    name: str
    message: str


class ListQuestion(QuestionBase):
    type: Literal["list"]
    choices: list[Choice]
    use_shortcuts: Optional[bool] = None


class SelectQuestion(QuestionBase):
    type: Literal["select"]
    choices: list[Choice]
    use_search_filter: Optional[bool] = None  # TODO: confirm type
    use_jk_keys: Optional[bool] = None


class InputQuestion(QuestionBase):
    type: Literal["input"]
    filter: Optional[Callable[[str], str]] = None


class ConfirmQuestion(QuestionBase):
    type: Literal["confirm"]
    default: Optional[bool] = None


CzQuestion = Union[ListQuestion, SelectQuestion, InputQuestion, ConfirmQuestion]


class CzQuestionModel(CzModel):
    question: CzQuestion = Field(discriminator="type")
