import os


import pytest

from commitizen import changelog


COMMIT_LOG = [
    "bump: version 1.5.0 → 1.5.1",
    "",
    "Merge pull request #29 from esciara/issue_28",
    "fix: #28 allows poetry add on py36 envs",
    "fix: #28 allows poetry add on py36 envs",
    "",
    "Merge pull request #26 from Woile/dependabot/pip/black-tw-19.3b0",
    "chore(deps-dev): update black requirement from ^18.3-alpha.0 to ^19.3b0",
    "Merge pull request #27 from Woile/dependabot/pip/mypy-tw-0.701",
    "chore(deps-dev): update mypy requirement from ^0.700.0 to ^0.701",
    "chore(deps-dev): update mypy requirement from ^0.700.0 to ^0.701",
    "Updates the requirements on [mypy](https://github.com/python/mypy) to permit the latest version.",
    "- [Release notes](https://github.com/python/mypy/releases)",
    "- [Commits](https://github.com/python/mypy/compare/v0.700...v0.701)",
    "",
    "Signed-off-by: dependabot[bot] <support@dependabot.com>",
    "chore(deps-dev): update black requirement from ^18.3-alpha.0 to ^19.3b0",
    "Updates the requirements on [black](https://github.com/ambv/black) to permit the latest version.",
    "- [Release notes](https://github.com/ambv/black/releases)",
    "- [Commits](https://github.com/ambv/black/commits)",
    "",
    "Signed-off-by: dependabot[bot] <support@dependabot.com>",
    "bump: version 1.4.0 → 1.5.0",
    "",
    "docs: add info about extra pattern in the files when bumping",
    "",
    "feat(bump): it is now possible to specify a pattern in the files attr to replace the version",
    "",
]

CHANGELOG_TEMPLATE = """
## 1.0.0 (2019-07-12)

### Bug fixes

- issue in poetry add preventing the installation in py36
- **users**: lorem ipsum apap


### Features

- it is possible to specify a pattern to be matched in configuration files bump.

## 0.9 (2019-07-11)

### Bug fixes

- holis

"""


@pytest.fixture
def existing_changelog_file(request):
    changelog_path = "tests/CHANGELOG.md"

    with open(changelog_path, "w") as f:
        f.write(CHANGELOG_TEMPLATE)

    yield changelog_path

    os.remove(changelog_path)


def test_read_changelog_blocks(existing_changelog_file):
    blocks = changelog.find_version_blocks(existing_changelog_file)
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
    ("### Bug fixes", {"category": "Bug fixes"}),
    ("### Features", {"category": "Features"}),
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
    ("### Bug fixes", {}),
    (
        "- name no longer accept invalid chars",
        {"message": "name no longer accept invalid chars", "scope": None},
    ),
    (
        "- **users**: lorem ipsum apap",
        {"message": "lorem ipsum apap", "scope": "users"},
    ),
]


@pytest.mark.parametrize("test_input,expected", VERSION_CASES)
def test_parse_md_version(test_input, expected):
    assert changelog.parse_md_version(test_input) == expected


@pytest.mark.parametrize("test_input,expected", CATEGORIES_CASES)
def test_parse_md_category(test_input, expected):
    assert changelog.parse_md_category(test_input) == expected


@pytest.mark.parametrize("test_input,expected", CATEGORIES_TRANSFORMATIONS)
def test_transform_category(test_input, expected):
    assert changelog.transform_category(test_input) == expected


@pytest.mark.parametrize("test_input,expected", MESSAGES_CASES)
def test_parse_md_message(test_input, expected):
    assert changelog.parse_md_message(test_input) == expected


def test_transform_category_fail():
    with pytest.raises(ValueError) as excinfo:
        changelog.transform_category("Bugs")
    assert "Could not match a category" in str(excinfo.value)


def test_generate_block_tree(existing_changelog_file):
    blocks = changelog.find_version_blocks(existing_changelog_file)
    block = next(blocks)
    tree = changelog.generate_block_tree(block)
    assert tree == {
        "commits": [
            {
                "scope": None,
                "message": "issue in poetry add preventing the installation in py36",
                "category": "fix",
            },
            {"scope": "users", "message": "lorem ipsum apap", "category": "fix"},
            {
                "scope": None,
                "message": "it is possible to specify a pattern to be matched in configuration files bump.",
                "category": "feat",
            },
        ],
        "version": "1.0.0",
        "date": "2019-07-12",
    }


def test_generate_full_tree(existing_changelog_file):
    blocks = changelog.find_version_blocks(existing_changelog_file)
    tree = list(changelog.generate_full_tree(blocks))

    assert tree == [
        {
            "commits": [
                {
                    "scope": None,
                    "message": "issue in poetry add preventing the installation in py36",
                    "category": "fix",
                },
                {"scope": "users", "message": "lorem ipsum apap", "category": "fix"},
                {
                    "scope": None,
                    "message": "it is possible to specify a pattern to be matched in configuration files bump.",
                    "category": "feat",
                },
            ],
            "version": "1.0.0",
            "date": "2019-07-12",
        },
        {
            "commits": [{"scope": None, "message": "holis", "category": "fix"}],
            "version": "0.9",
            "date": "2019-07-11",
        },
    ]
