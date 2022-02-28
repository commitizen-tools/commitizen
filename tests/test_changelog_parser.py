import os

import pytest

from commitizen import changelog_parser

CHANGELOG_TEMPLATE = """
## 1.0.0 (2019-07-12)

### Fix

- issue in poetry add preventing the installation in py36
- **users**: lorem ipsum apap

### Feat

- it is possible to specify a pattern to be matched in configuration files bump.

## 0.9 (2019-07-11)

### Fix

- holis

"""


@pytest.fixture
def changelog_content() -> str:
    changelog_path = "tests/CHANGELOG_FOR_TEST.md"
    with open(changelog_path, "r") as f:
        return f.read()


@pytest.fixture
def existing_changelog_file(tmpdir):
    with tmpdir.as_cwd():
        changelog_path = os.path.join(os.getcwd(), "CHANGELOG.md")
        # changelog_path = "tests/CHANGELOG.md"

        with open(changelog_path, "w") as f:
            f.write(CHANGELOG_TEMPLATE)

        yield changelog_path

        os.remove(changelog_path)


def test_read_changelog_blocks(existing_changelog_file):
    blocks = changelog_parser.find_version_blocks(existing_changelog_file)
    blocks = list(blocks)
    amount_of_blocks = len(blocks)
    assert amount_of_blocks == 2


VERSION_CASES: list = [
    ("## 1.0.0 (2019-07-12)", {"version": "1.0.0", "date": "2019-07-12"}),
    ("## 2.3.0a0", {"version": "2.3.0a0", "date": None}),
    ("## 0.10.0a0", {"version": "0.10.0a0", "date": None}),
    ("## 1.0.0rc0", {"version": "1.0.0rc0", "date": None}),
    ("## 1beta", {"version": "1beta", "date": None}),
    (
        "## 1.0.0rc1+e20d7b57f3eb (2019-3-24)",
        {"version": "1.0.0rc1+e20d7b57f3eb", "date": "2019-3-24"},
    ),
    ("### Bug fixes", {}),
    ("- issue in poetry add preventing the installation in py36", {}),
]

CATEGORIES_CASES: list = [
    ("## 1.0.0 (2019-07-12)", {}),
    ("## 2.3.0a0", {}),
    ("### Bug fixes", {"change_type": "Bug fixes"}),
    ("### Features", {"change_type": "Features"}),
    ("- issue in poetry add preventing the installation in py36", {}),
]

CATEGORIES_TRANSFORMATIONS: list = [
    ("Bug fixes", "fix"),
    ("Features", "feat"),
    ("BREAKING CHANGES", "BREAKING CHANGES"),
]

MESSAGES_CASES: list = [
    ("## 1.0.0 (2019-07-12)", {}),
    ("## 2.3.0a0", {}),
    ("### Fix", {}),
    (
        "- name no longer accept invalid chars",
        {
            "message": "name no longer accept invalid chars",
            "scope": None,
            "breaking": None,
        },
    ),
    (
        "- **users**: lorem ipsum apap",
        {"message": "lorem ipsum apap", "scope": "users", "breaking": None},
    ),
]


@pytest.mark.parametrize("test_input,expected", VERSION_CASES)
def test_parse_md_version(test_input, expected):
    assert changelog_parser.parse_md_version(test_input) == expected


@pytest.mark.parametrize("test_input,expected", CATEGORIES_CASES)
def test_parse_md_change_type(test_input, expected):
    assert changelog_parser.parse_md_change_type(test_input) == expected


@pytest.mark.parametrize("test_input,expected", CATEGORIES_TRANSFORMATIONS)
def test_transform_change_type(test_input, expected):
    assert changelog_parser.transform_change_type(test_input) == expected


@pytest.mark.parametrize("test_input,expected", MESSAGES_CASES)
def test_parse_md_message(test_input, expected):
    assert changelog_parser.parse_md_message(test_input) == expected


def test_transform_change_type_fail():
    with pytest.raises(ValueError) as excinfo:
        changelog_parser.transform_change_type("Bugs")
    assert "Could not match a change_type" in str(excinfo.value)


def test_generate_block_tree(existing_changelog_file):
    blocks = changelog_parser.find_version_blocks(existing_changelog_file)
    block = next(blocks)
    tree = changelog_parser.generate_block_tree(block)
    assert tree == {
        "changes": {
            "fix": [
                {
                    "scope": None,
                    "breaking": None,
                    "message": "issue in poetry add preventing the installation in py36",
                },
                {"scope": "users", "breaking": None, "message": "lorem ipsum apap"},
            ],
            "feat": [
                {
                    "scope": None,
                    "breaking": None,
                    "message": (
                        "it is possible to specify a pattern to be matched "
                        "in configuration files bump."
                    ),
                }
            ],
        },
        "version": "1.0.0",
        "date": "2019-07-12",
    }


def test_generate_full_tree(existing_changelog_file):
    blocks = changelog_parser.find_version_blocks(existing_changelog_file)
    tree = list(changelog_parser.generate_full_tree(blocks))

    assert tree == [
        {
            "changes": {
                "fix": [
                    {
                        "scope": None,
                        "message": "issue in poetry add preventing the installation in py36",
                        "breaking": None,
                    },
                    {"scope": "users", "message": "lorem ipsum apap", "breaking": None},
                ],
                "feat": [
                    {
                        "scope": None,
                        "message": "it is possible to specify a pattern to be matched in configuration files bump.",
                        "breaking": None,
                    }
                ],
            },
            "version": "1.0.0",
            "date": "2019-07-12",
        },
        {
            "changes": {"fix": [{"scope": None, "message": "holis", "breaking": None}]},
            "version": "0.9",
            "date": "2019-07-11",
        },
    ]
