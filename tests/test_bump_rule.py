import pytest

from commitizen.bump_rule import (
    ConventionalCommitBumpRule,
    OldSchoolBumpRule,
    find_increment_by_callable,
)
from commitizen.defaults import (
    BUMP_MAP,
    BUMP_MAP_MAJOR_VERSION_ZERO,
    BUMP_PATTERN,
    MAJOR,
    MINOR,
    PATCH,
)
from commitizen.exceptions import NoPatternMapError


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
        assert bump_rule.get_increment("feat!: breaking change", False) == MAJOR
        assert bump_rule.get_increment("feat!: breaking change", True) == MINOR

    def test_breaking_change_type(self, bump_rule):
        assert bump_rule.get_increment("BREAKING CHANGE: major change", False) == MAJOR
        assert bump_rule.get_increment("BREAKING CHANGE: major change", True) == MINOR

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
            == MAJOR
        )
        assert (
            bump_rule.get_increment("feat(api)!: remove deprecated endpoints", True)
            == MINOR
        )

        # Test with BREAKING CHANGE and scopes
        assert (
            bump_rule.get_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", False
            )
            == MAJOR
        )
        assert (
            bump_rule.get_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", True
            )
            == MINOR
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
        assert find_increment_by_callable(commit_messages, get_increment) == MAJOR

    def test_multi_line_commit(self, get_increment):
        commit_messages = [
            "feat: new feature\n\nBREAKING CHANGE: major change",
        ]
        assert find_increment_by_callable(commit_messages, get_increment) == MAJOR

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
            == MINOR
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


class TestOldSchoolBumpRule:
    @pytest.fixture
    def bump_pattern(self):
        return r"^.*?\[(.*?)\].*$"

    @pytest.fixture
    def bump_map(self):
        return {
            "MAJOR": MAJOR,
            "MINOR": MINOR,
            "PATCH": PATCH,
        }

    @pytest.fixture
    def bump_map_major_version_zero(self):
        return {
            "MAJOR": MINOR,  # MAJOR becomes MINOR in version zero
            "MINOR": MINOR,
            "PATCH": PATCH,
        }

    @pytest.fixture
    def old_school_rule(self, bump_pattern, bump_map, bump_map_major_version_zero):
        return OldSchoolBumpRule(bump_pattern, bump_map, bump_map_major_version_zero)

    def test_major_version(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat: add new feature [MAJOR]", False)
            == MAJOR
        )
        assert old_school_rule.get_increment("fix: bug fix [MAJOR]", False) == MAJOR

    def test_minor_version(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat: add new feature [MINOR]", False)
            == MINOR
        )
        assert old_school_rule.get_increment("fix: bug fix [MINOR]", False) == MINOR

    def test_patch_version(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat: add new feature [PATCH]", False)
            == PATCH
        )
        assert old_school_rule.get_increment("fix: bug fix [PATCH]", False) == PATCH

    def test_major_version_zero(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat: add new feature [MAJOR]", True)
            == MINOR
        )
        assert old_school_rule.get_increment("fix: bug fix [MAJOR]", True) == MINOR

    def test_no_match(self, old_school_rule):
        assert old_school_rule.get_increment("feat: add new feature", False) is None
        assert old_school_rule.get_increment("fix: bug fix", False) is None

    def test_invalid_pattern(self, bump_map, bump_map_major_version_zero):
        with pytest.raises(NoPatternMapError):
            OldSchoolBumpRule("", bump_map, bump_map_major_version_zero)

    def test_invalid_bump_map(self, bump_pattern):
        with pytest.raises(NoPatternMapError):
            OldSchoolBumpRule(bump_pattern, {}, {})

    def test_invalid_bump_map_major_version_zero(self, bump_pattern, bump_map):
        with pytest.raises(NoPatternMapError):
            OldSchoolBumpRule(bump_pattern, bump_map, {})

    def test_all_invalid(self):
        with pytest.raises(NoPatternMapError):
            OldSchoolBumpRule("", {}, {})

    def test_none_values(self):
        with pytest.raises(NoPatternMapError):
            OldSchoolBumpRule(None, {}, {})

    def test_empty_pattern_with_valid_maps(self, bump_map, bump_map_major_version_zero):
        with pytest.raises(NoPatternMapError):
            OldSchoolBumpRule("", bump_map, bump_map_major_version_zero)

    def test_empty_maps_with_valid_pattern(self, bump_pattern):
        with pytest.raises(NoPatternMapError):
            OldSchoolBumpRule(bump_pattern, {}, {})

    def test_complex_pattern(self):
        pattern = r"^.*?\[(.*?)\].*?\[(.*?)\].*$"
        bump_map = {
            "MAJOR": MAJOR,
            "MINOR": MINOR,
            "PATCH": PATCH,
        }
        rule = OldSchoolBumpRule(pattern, bump_map, bump_map)

        assert (
            rule.get_increment("feat: add new feature [MAJOR] [MINOR]", False) == MAJOR
        )
        assert rule.get_increment("fix: bug fix [MINOR] [PATCH]", False) == MINOR

    def test_with_find_increment_by_callable(self, old_school_rule):
        commit_messages = [
            "feat: add new feature [MAJOR]",
            "fix: bug fix [PATCH]",
            "docs: update readme [MINOR]",
        ]
        assert (
            find_increment_by_callable(
                commit_messages, lambda x: old_school_rule.get_increment(x, False)
            )
            == MAJOR
        )


class TestOldSchoolBumpRuleWithDefault:
    @pytest.fixture
    def old_school_rule(self):
        return OldSchoolBumpRule(BUMP_PATTERN, BUMP_MAP, BUMP_MAP_MAJOR_VERSION_ZERO)

    def test_breaking_change_with_bang(self, old_school_rule):
        assert old_school_rule.get_increment("feat!: breaking change", False) == MAJOR
        assert old_school_rule.get_increment("fix!: breaking change", False) == MAJOR
        assert old_school_rule.get_increment("feat!: breaking change", True) == MINOR
        assert old_school_rule.get_increment("fix!: breaking change", True) == MINOR

    def test_breaking_change_type(self, old_school_rule):
        assert (
            old_school_rule.get_increment("BREAKING CHANGE: major change", False)
            == MAJOR
        )
        assert (
            old_school_rule.get_increment("BREAKING-CHANGE: major change", False)
            == MAJOR
        )
        assert (
            old_school_rule.get_increment("BREAKING CHANGE: major change", True)
            == MINOR
        )
        assert (
            old_school_rule.get_increment("BREAKING-CHANGE: major change", True)
            == MINOR
        )

    def test_feat_commit(self, old_school_rule):
        assert old_school_rule.get_increment("feat: add new feature", False) == MINOR
        assert old_school_rule.get_increment("feat: add new feature", True) == MINOR

    def test_fix_commit(self, old_school_rule):
        assert old_school_rule.get_increment("fix: fix bug", False) == PATCH
        assert old_school_rule.get_increment("fix: fix bug", True) == PATCH

    def test_refactor_commit(self, old_school_rule):
        assert (
            old_school_rule.get_increment("refactor: restructure code", False) == PATCH
        )
        assert (
            old_school_rule.get_increment("refactor: restructure code", True) == PATCH
        )

    def test_perf_commit(self, old_school_rule):
        assert (
            old_school_rule.get_increment("perf: improve performance", False) == PATCH
        )
        assert old_school_rule.get_increment("perf: improve performance", True) == PATCH

    def test_commit_with_scope(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat(api): add new endpoint", False) == MINOR
        )
        assert (
            old_school_rule.get_increment("fix(ui): fix button alignment", False)
            == PATCH
        )
        assert (
            old_school_rule.get_increment("refactor(core): restructure", False) == PATCH
        )

    def test_no_match(self, old_school_rule):
        assert (
            old_school_rule.get_increment("docs: update documentation", False) is None
        )
        assert old_school_rule.get_increment("style: format code", False) is None
        assert old_school_rule.get_increment("test: add unit tests", False) is None
        assert (
            old_school_rule.get_increment("build: update build config", False) is None
        )
        assert old_school_rule.get_increment("ci: update CI pipeline", False) is None

    def test_with_find_increment_by_callable(self, old_school_rule):
        commit_messages = [
            "feat!: breaking change",
            "fix: bug fix",
            "perf: improve performance",
        ]
        assert (
            find_increment_by_callable(
                commit_messages, lambda x: old_school_rule.get_increment(x, False)
            )
            == MAJOR
        )
