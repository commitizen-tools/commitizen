# Testing your Commitizen plugin

Adding a test suite to your plugin helps prevent accidental regressions when you update
commit rules, regex patterns, or changelog templates. This guide shows how to test the
most common plugin behaviors using [pytest](https://docs.pytest.org/).

## Setup

Install the testing dependencies in your plugin project:

```bash
pip install commitizen pytest
```

## Testing commit message rules

### Testing `bump_pattern` and `bump_map`

Use `commitizen.bump.find_increment` to verify that your regex correctly maps commit
messages to the expected version increment (`MAJOR`, `MINOR`, `PATCH`, or `None`).

```python title="tests/test_my_plugin.py"
import pytest
from commitizen import bump
from commitizen.git import GitCommit

from my_plugin import MyCommitizen  # replace with your plugin import


def make_commits(*messages: str) -> list[GitCommit]:
    return [GitCommit(rev="abc123", title=msg) for msg in messages]


@pytest.mark.parametrize(
    ("messages", "expected"),
    [
        # patch — bug fixes should produce a PATCH bump
        (["fix: correct off-by-one error"], "PATCH"),
        # minor — new features should produce a MINOR bump
        (["feat: add dark mode"], "MINOR"),
        # major — breaking changes should produce a MAJOR bump
        (["feat!: rename public API"], "MAJOR"),
        # no relevant commits — no bump
        (["chore: update CI config"], None),
    ],
)
def test_bump_increment(messages, expected):
    commits = make_commits(*messages)
    result = bump.find_increment(
        commits,
        regex=MyCommitizen.bump_pattern,
        increments_map=MyCommitizen.bump_map,
    )
    assert result == expected
```

### Testing `changelog_pattern` and `commit_parser`

Verify that only relevant commits appear in the changelog and that the parser
extracts fields (type, scope, message) correctly.

```python title="tests/test_changelog_rules.py"
import re

from my_plugin import MyCommitizen


@pytest.mark.parametrize(
    ("message", "should_match"),
    [
        ("feat(api): add pagination", True),
        ("fix: handle null pointer", True),
        ("chore: bump dev dependency", False),
        ("docs: update README", False),
    ],
)
def test_changelog_pattern(message, should_match):
    pattern = re.compile(MyCommitizen.changelog_pattern)
    assert bool(pattern.match(message)) is should_match


@pytest.mark.parametrize(
    ("message", "expected_groups"),
    [
        (
            "feat(api): add pagination",
            {"change_type": "feat", "scope": "api", "message": "add pagination"},
        ),
        (
            "fix: handle null pointer",
            {"change_type": "fix", "scope": None, "message": "handle null pointer"},
        ),
    ],
)
def test_commit_parser(message, expected_groups):
    pattern = re.compile(MyCommitizen.commit_parser)
    match = pattern.match(message)
    assert match is not None
    for key, value in expected_groups.items():
        assert match.group(key) == value
```

### Testing `message()` output

Ensure your `message()` method produces the correct commit string from user answers.

```python title="tests/test_message.py"
from commitizen.config import BaseConfig

from my_plugin import MyCommitizen


def test_message_with_scope():
    cz = MyCommitizen(BaseConfig())
    msg = cz.message({"type": "feat", "scope": "api", "subject": "add pagination"})
    assert msg == "feat(api): add pagination"


def test_message_without_scope():
    cz = MyCommitizen(BaseConfig())
    msg = cz.message({"type": "fix", "scope": "", "subject": "handle null pointer"})
    assert msg == "fix: handle null pointer"
```

## Testing schema validation

If your plugin overrides `schema_pattern()`, test that valid and invalid commit
messages are accepted and rejected as expected.

```python title="tests/test_schema.py"
import re

from my_plugin import MyCommitizen


def test_valid_commit_passes_schema():
    pattern = re.compile(MyCommitizen().schema_pattern())
    assert pattern.match("feat(api): add pagination")


def test_invalid_commit_fails_schema():
    pattern = re.compile(MyCommitizen().schema_pattern())
    assert not pattern.match("random text without type")
```

## Running the tests

```bash
pytest tests/ -v
```

## See also

- [Customizing through a Python class](python_class.md) — full plugin API reference
- [Third-Party Commitizen Plugins](../third-party-plugins/about.md) — examples of published plugins
- [Commitizen's own test suite](https://github.com/commitizen-tools/commitizen/tree/master/tests) — for more advanced testing patterns
