import pytest

from commitizen.bump_rule import DefaultBumpRule
from commitizen.defaults import MAJOR, MINOR, PATCH


@pytest.fixture
def bump_rule():
    return DefaultBumpRule()


class TestDefaultBumpRule:
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
