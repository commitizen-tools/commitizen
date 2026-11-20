# Testing plugins

Automated tests catch regressions when you change a plugin's rules or upgrade
Commitizen. Start with tests for version bumps, changelog extraction, message
creation, and validation. These tests do not need interactive prompts or a Git
repository.

## Set up a test plugin

Install `pytest` in your plugin's development environment. For an existing
packaged plugin, install it in editable mode as well:

```sh
python -m pip install -e . pytest
```

For the standalone example below, install `commitizen` and `pytest`, then create
`cz_example.py` and `tests/test_plugin.py` in the same project directory. Use the
Commitizen version that your plugin supports. The bump tests below use
`commitizen.version_increment.VersionIncrement`; older versions may instead
provide `commitizen.bump.find_increment` with a different return type.

This example uses `major`, `minor`, and `patch` prefixes. A `docs` message is
valid but does not cause a version bump or appear in the changelog. These are
example rules, not requirements for every plugin.

```python title="cz_example.py"
from collections.abc import Mapping
from typing import Any

from commitizen.cz.base import BaseCommitizen
from commitizen.question import CzQuestion


class ExampleCommitizen(BaseCommitizen):
    """Use explicit version increments as commit prefixes.

    Attributes:
        config: Configuration supplied to the inherited constructor.
        bump_pattern: Pattern whose first group selects a bump token.
        bump_map: Mapping from bump tokens to version increments.
        changelog_pattern: Pattern selecting commits for the changelog.
        commit_parser: Pattern extracting changelog fields.

    Example:
        ```python
        from commitizen.config import BaseConfig

        plugin = ExampleCommitizen(BaseConfig())
        plugin.message({"prefix": "patch", "subject": "repair login"})
        ```
    """

    bump_pattern = r"^(major|minor|patch): "
    bump_map = {"major": "MAJOR", "minor": "MINOR", "patch": "PATCH"}
    changelog_pattern = r"^(major|minor|patch): "
    commit_parser = r"^(?P<change_type>major|minor|patch): (?P<message>[^\r\n]+)"

    def questions(self) -> list[CzQuestion]:
        """Ask for the prefix and subject used to build a message."""
        return [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the change type",
                "choices": ["major", "minor", "patch", "docs"],
            },
            {"type": "input", "name": "subject", "message": "Commit subject"},
        ]

    def message(self, answers: Mapping[str, Any]) -> str:
        """Build a commit message from the supplied answers."""
        return f"{answers['prefix']}: {answers['subject'].strip()}"

    def example(self) -> str:
        """Show a valid commit message."""
        return "patch: repair login"

    def schema(self) -> str:
        """Describe the accepted single-line message format."""
        return "<major|minor|patch|docs>: <subject>"

    def schema_pattern(self) -> str:
        """Require a known prefix and a non-empty single-line subject."""
        return r"\A(major|minor|patch|docs): [^\s\r\n][^\r\n]*\Z"

    def info(self) -> str:
        """Explain the example's versioning rules."""
        return "Use major for breaking changes, minor for features, patch for fixes."
```

Add these imports and a fixture to `tests/test_plugin.py`. A fixture supplies a
fresh plugin instance for each test. Define it in your own project; Commitizen's
repository fixtures are not installed with the package.

```python title="tests/test_plugin.py"
import re

import pytest

from commitizen.changelog import generate_tree_from_commits
from commitizen.config import BaseConfig
from commitizen.git import GitCommit
from commitizen.version_increment import VersionIncrement
from cz_example import ExampleCommitizen


@pytest.fixture
def plugin() -> ExampleCommitizen:
    """Keep configuration changes isolated between tests."""
    return ExampleCommitizen(BaseConfig())
```

Append the following four examples to that test file. Replace the example class
and expected results with your own plugin's rules.

## Test version bumps

`bump_pattern` extracts a token in its first capture group. `bump_map` maps that
token to an increment. Test the result through Commitizen's calculation rather
than only checking that the regular expression matches.

`pytest.mark.parametrize` runs the test once for each input and expected result.
Include all increments, no matching commits, an empty input, and mixed commits
to check that the highest increment wins. This helper returns
`VersionIncrement.NONE` when no bump is needed.

```python
@pytest.mark.parametrize(
    ("messages", "expected"),
    [
        (["patch: repair login"], VersionIncrement.PATCH),
        (["minor: add export"], VersionIncrement.MINOR),
        (["major: remove old API"], VersionIncrement.MAJOR),
        (["docs: update README"], VersionIncrement.NONE),
        (["patchwork: unrelated text"], VersionIncrement.NONE),
        ([], VersionIncrement.NONE),
        (["patch: repair login", "minor: add export"], VersionIncrement.MINOR),
        (["major: remove old API", "patch: repair login"], VersionIncrement.MAJOR),
    ],
)
def test_bump(
    plugin: ExampleCommitizen, messages: list[str], expected: VersionIncrement
) -> None:
    """Check version increments, including precedence and ignored messages."""
    # Arrange
    pattern = plugin.bump_pattern
    bump_map = plugin.bump_map

    # Act
    increment = VersionIncrement.get_highest_by_messages(messages, pattern, bump_map)

    # Assert
    assert increment == expected
```

If your plugin supports breaking-change footers or `bump_map_major_version_zero`,
add cases for those rules too. This example does not define those features.

## Test changelog extraction

`changelog_pattern` decides which commits are eligible. `commit_parser` extracts
named fields such as `change_type` and `message`. A match in the first pattern
alone does not guarantee that a changelog entry is produced.

Pass in-memory commits to the changelog generator to test both rules together.
An empty tag list puts the results in the `Unreleased` section. No real commits
are created. Check the extracted text as well as which entries are excluded.

```python
@pytest.mark.parametrize(
    ("title", "body", "expected"),
    [
        ("patch: repair login", "", {"patch": ["repair login"]}),
        ("minor: add export", "", {"minor": ["add export"]}),
        ("major: remove old API", "", {"major": ["remove old API"]}),
        ("docs: update README", "", {}),
        ("patchwork: unrelated text", "", {}),
        ("patch: ", "", {}),
        ("patch: repair login", "Additional context.", {"patch": ["repair login"]}),
    ],
)
def test_changelog(
    plugin: ExampleCommitizen,
    title: str,
    body: str,
    expected: dict[str, list[str]],
) -> None:
    """Check filtering and parsing, including a commit with a body."""
    # Arrange
    commits = [GitCommit(rev="abc123", title=title, body=body)]

    # Act
    releases = list(
        generate_tree_from_commits(
            commits=commits,
            tags=[],
            commit_parser=plugin.commit_parser,
            changelog_pattern=plugin.changelog_pattern,
        )
    )
    changes = {
        kind: [entry["message"] for entry in entries]
        for kind, entries in releases[0]["changes"].items()
    }

    # Assert
    assert len(releases) == 1
    assert releases[0]["version"] == "Unreleased"
    assert changes == expected
```

If your plugin defines `change_type_map` or changelog hooks, pass them to the
generator and assert their effect. Add separate output tests if you customize
rendering; this example checks extracted entries, not rendered Markdown.

## Test message creation

Call `message()` with a dictionary of answers instead of opening an interactive
prompt. Assert the exact string, including spacing and any body or footer your
plugin supports.

```python
def test_message(plugin: ExampleCommitizen) -> None:
    """Check message formatting and removal of surrounding subject whitespace."""
    # Arrange
    answers = {"prefix": "patch", "subject": " repair login "}

    # Act
    message = plugin.message(answers)

    # Assert
    assert message == "patch: repair login"
```

## Test the validation pattern

Check both accepted and rejected messages. Also check that `example()` and
`message()` produce messages accepted by the pattern. Use `re.match`, as
Commitizen's default message validator does. Anchors in this example's pattern
reject additional lines.

```python
@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("patch: repair login", True),
        ("docs: update README", True),
        ("unknown: repair login", False),
        ("patch repair login", False),
        ("patch: ", False),
        ("", False),
        ("patch: repair login\nextra text", False),
    ],
)
def test_schema(plugin: ExampleCommitizen, message: str, expected: bool) -> None:
    """Check the plugin's accepted and rejected message formats."""
    # Arrange
    pattern = plugin.schema_pattern()

    # Act
    valid = re.match(pattern, message) is not None

    # Assert
    assert valid is expected


def test_generated_messages_match_schema(plugin: ExampleCommitizen) -> None:
    """Keep the plugin's example, message builder, and schema consistent."""
    # Arrange
    answers = {"prefix": "patch", "subject": "repair login"}
    pattern = plugin.schema_pattern()

    # Act
    messages = [plugin.example(), plugin.message(answers)]

    # Assert
    assert all(re.match(pattern, message) is not None for message in messages)
```

These tests cover the schema pattern, not all `cz check` options, such as message
length limits or allowed prefixes. If you override `validate_commit_message`,
also test that method's results and errors.

## Run and extend the tests

From your plugin project directory, run:

```sh
python -m pytest tests/test_plugin.py
```

Run these tests in continuous integration against the Commitizen versions you
support. The bump and changelog helpers are implementation APIs; check their
signatures when upgrading your dependency.

These examples instantiate the class directly. They do not verify package
installation or `commitizen.plugin` entry-point discovery. For a packaged
plugin, also install it in a clean environment and check that
`cz -n YOUR_PLUGIN_NAME example` loads the intended plugin. For Git-dependent
command tests, use a temporary repository, never your working repository.

For more examples, see Commitizen's
[version increment tests](https://github.com/commitizen-tools/commitizen/blob/master/tests/test_version_increment.py),
[changelog tests](https://github.com/commitizen-tools/commitizen/blob/master/tests/test_changelog.py),
and [commit message tests](https://github.com/commitizen-tools/commitizen/blob/master/tests/test_cz_conventional_commits.py).
