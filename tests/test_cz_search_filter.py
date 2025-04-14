import pytest

from commitizen.config import TomlConfig
from commitizen.cz.customize import CustomizeCommitsCz

TOML_WITH_SEARCH_FILTER = r"""
[tool.commitizen]
name = "cz_customize"

[tool.commitizen.customize]
message_template = "{{change_type}}:{% if scope %} ({{scope}}){% endif %}{% if breaking %}!{% endif %} {{message}}"

[[tool.commitizen.customize.questions]]
type = "select"
name = "change_type"
message = "Select the type of change you are committing"
use_search_filter = true
use_jk_keys = false
choices = [
    {value = "fix", name = "fix: A bug fix. Correlates with PATCH in SemVer"},
    {value = "feat", name = "feat: A new feature. Correlates with MINOR in SemVer"},
    {value = "docs", name = "docs: Documentation only changes"},
    {value = "style", name = "style: Changes that do not affect the meaning of the code"},
    {value = "refactor", name = "refactor: A code change that neither fixes a bug nor adds a feature"},
    {value = "perf", name = "perf: A code change that improves performance"},
    {value = "test", name = "test: Adding missing or correcting existing tests"},
    {value = "build", name = "build: Changes that affect the build system or external dependencies"},
    {value = "ci", name = "ci: Changes to CI configuration files and scripts"}
]

[[tool.commitizen.customize.questions]]
type = "input"
name = "scope"
message = "What is the scope of this change? (class or file name): (press [enter] to skip)"

[[tool.commitizen.customize.questions]]
type = "input"
name = "message"
message = "Write a short and imperative summary of the code changes: (lower case and no period)"
"""


@pytest.fixture
def config():
    return TomlConfig(data=TOML_WITH_SEARCH_FILTER, path="not_exist.toml")


def test_questions_with_search_filter(config):
    """Test that questions are properly configured with search filter"""
    cz = CustomizeCommitsCz(config)
    questions = cz.questions()

    # Test that the first question (change_type) has search filter enabled
    assert questions[0]["type"] == "select"
    assert questions[0]["name"] == "change_type"
    assert questions[0]["use_search_filter"] is True
    assert questions[0]["use_jk_keys"] is False

    # Test that the choices are properly configured
    choices = questions[0]["choices"]
    assert len(choices) == 9  # We have 9 commit types
    assert choices[0]["value"] == "fix"
    assert choices[1]["value"] == "feat"


def test_message_template(config):
    """Test that the message template is properly configured"""
    cz = CustomizeCommitsCz(config)
    template = cz.message(
        {
            "change_type": "feat",
            "scope": "search",
            "message": "add search filter support",
        }
    )
    assert template == "feat: (search) add search filter support"
