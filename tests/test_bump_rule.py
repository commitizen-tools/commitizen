import pytest

from commitizen.bump_rule import ConventionalCommitBumpRule, find_increment_by_callable
from commitizen.defaults import MAJOR, MINOR, PATCH


@pytest.fixture
def bump_rule():
    return ConventionalCommitBumpRule()


class TestConventionalCommitBumpRule:
    def test_feat_commit(self, bump_rule):
        assert bump_rule.get_increment("feat: add new feature", False) == MINOR
        assert bump_rule.get_increment("feat: add new feature", True) == MINOR

    def test_fix_commit(self, bump_rule):
        assert bump_rule.get_increment("fix: fix bug", False) == PATCH
        assert bump_rule.get_increment("fix: fix bug", True) == PATCH

    def test_perf_commit(self, bump_rule):
        assert bump_rule.get_increment("perf: improve performance", False) == PATCH
        assert bump_rule.get_increment("perf: improve performance", True) == PATCH

    def test_refactor_commit(self, bump_rule):
        assert bump_rule.get_increment("refactor: restructure code", False) == PATCH
        assert bump_rule.get_increment("refactor: restructure code", True) == PATCH

    def test_breaking_change_with_bang(self, bump_rule):
        assert bump_rule.get_increment("feat!: breaking change", False) == MINOR
        assert bump_rule.get_increment("feat!: breaking change", True) == MAJOR

    def test_breaking_change_type(self, bump_rule):
        assert bump_rule.get_increment("BREAKING CHANGE: major change", False) == MINOR
        assert bump_rule.get_increment("BREAKING CHANGE: major change", True) == MAJOR

    def test_commit_with_scope(self, bump_rule):
        assert bump_rule.get_increment("feat(api): add new endpoint", False) == MINOR
        assert bump_rule.get_increment("fix(ui): fix button alignment", False) == PATCH

    def test_commit_with_complex_scopes(self, bump_rule):
        # Test with multiple word scopes
        assert (
            bump_rule.get_increment("feat(user_management): add user roles", False)
            == MINOR
        )
        assert (
            bump_rule.get_increment("fix(database_connection): handle timeout", False)
            == PATCH
        )

        # Test with nested scopes
        assert (
            bump_rule.get_increment("feat(api/auth): implement OAuth", False) == MINOR
        )
        assert (
            bump_rule.get_increment("fix(ui/components): fix dropdown", False) == PATCH
        )

        # Test with breaking changes and scopes
        assert (
            bump_rule.get_increment("feat(api)!: remove deprecated endpoints", False)
            == MINOR
        )
        assert (
            bump_rule.get_increment("feat(api)!: remove deprecated endpoints", True)
            == MAJOR
        )

        # Test with BREAKING CHANGE and scopes
        assert (
            bump_rule.get_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", False
            )
            == MINOR
        )
        assert (
            bump_rule.get_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", True
            )
            == MAJOR
        )

    def test_invalid_commit_message(self, bump_rule):
        assert bump_rule.get_increment("invalid commit message", False) is None
        assert bump_rule.get_increment("", False) is None
        assert bump_rule.get_increment("feat", False) is None

    def test_other_commit_types(self, bump_rule):
        # These commit types should not trigger any version bump
        assert bump_rule.get_increment("docs: update documentation", False) is None
        assert bump_rule.get_increment("style: format code", False) is None
        assert bump_rule.get_increment("test: add unit tests", False) is None
        assert bump_rule.get_increment("build: update build config", False) is None
        assert bump_rule.get_increment("ci: update CI pipeline", False) is None


class TestFindIncrementByCallable:
    @pytest.fixture
    def get_increment(self, bump_rule):
        return lambda x: bump_rule.get_increment(x, False)

    def test_single_commit(self, get_increment):
        commit_messages = ["feat: add new feature"]
        assert find_increment_by_callable(commit_messages, get_increment) == MINOR

    def test_multiple_commits(self, get_increment):
        commit_messages = [
            "feat: new feature",
            "fix: bug fix",
            "docs: update readme",
        ]
        assert find_increment_by_callable(commit_messages, get_increment) == MINOR

    def test_breaking_change(self, get_increment):
        commit_messages = [
            "feat: new feature",
            "feat!: breaking change",
        ]
        assert find_increment_by_callable(commit_messages, get_increment) == MINOR

    def test_multi_line_commit(self, get_increment):
        commit_messages = [
            "feat: new feature\n\nBREAKING CHANGE: major change",
        ]
        assert find_increment_by_callable(commit_messages, get_increment) == MINOR

    def test_no_increment_needed(self, get_increment):
        commit_messages = [
            "docs: update documentation",
            "style: format code",
        ]
        assert find_increment_by_callable(commit_messages, get_increment) is None

    def test_empty_commits(self, get_increment):
        commit_messages = []
        assert find_increment_by_callable(commit_messages, get_increment) is None

    def test_major_version_zero(self):
        bump_rule = ConventionalCommitBumpRule()

        commit_messages = [
            "feat!: breaking change",
            "BREAKING CHANGE: major change",
        ]
        assert (
            find_increment_by_callable(
                commit_messages, lambda x: bump_rule.get_increment(x, True)
            )
            == MAJOR
        )

    def test_mixed_commit_types(self, get_increment):
        commit_messages = [
            "feat: new feature",
            "fix: bug fix",
            "perf: improve performance",
            "refactor: restructure code",
        ]
        assert find_increment_by_callable(commit_messages, get_increment) == MINOR

    def test_commit_with_scope(self, get_increment):
        commit_messages = [
            "feat(api): add new endpoint",
            "fix(ui): fix button alignment",
        ]
        assert find_increment_by_callable(commit_messages, get_increment) == MINOR
