from collections.abc import Iterable
from typing import Generic, TypeVar

T = TypeVar("T")


class UniqueList(Generic[T]):
    def __init__(self, items: list[T]):
        if len(items) != len(set(items)):
            raise ValueError("Items must be unique")
        self._items = items

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __repr__(self):
        return f"UniqueList({self._items})"

    def __add__(self, other: Iterable[T]) -> "UniqueList[T]":
        # Support UniqueList + list or UniqueList + UniqueList
        combined = self._items + list(other)
        return UniqueList(combined)

    def __radd__(self, other: Iterable[T]) -> "UniqueList[T]":
        combined = list(other) + self._items
        return UniqueList(combined)

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, item: T) -> bool:
        return item in self._items

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UniqueList) and self._items == other._items
