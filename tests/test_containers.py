import pytest

from commitizen.containers import UniqueList


def test_unique_list():
    # Test initialization with unique items
    unique_list = UniqueList([1, 2, 3])
    assert list(unique_list) == [1, 2, 3]

    # Test initialization with duplicate items
    with pytest.raises(ValueError, match="Items must be unique"):
        UniqueList([1, 1, 2])

    # Test iteration
    items = [1, 2, 3]
    unique_list = UniqueList(items)
    assert [x for x in unique_list] == items

    # Test indexing
    assert unique_list[0] == 1
    assert unique_list[1] == 2
    assert unique_list[2] == 3

    # Test string representation
    assert repr(unique_list) == "UniqueList([1, 2, 3])"

    # Test with different types
    string_list = UniqueList(["a", "b", "c"])
    assert list(string_list) == ["a", "b", "c"]

    # Test add
    assert unique_list + [4, 5, 6] == UniqueList([1, 2, 3, 4, 5, 6])
    assert [4, 5, 6] + unique_list == UniqueList([4, 5, 6, 1, 2, 3])

    # Test contains
    assert 1 in unique_list
    assert 3 in unique_list
    assert 7 not in unique_list

    # Test len
    assert len(unique_list) == 3
