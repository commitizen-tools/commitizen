import pytest

from commitizen.bump_rule import (
    ConventionalCommitBumpRule,
    OldSchoolBumpRule,
    SemVerIncrement,
    _find_highest_increment,
    find_increment_by_callable,
)
from commitizen.defaults import (
    BUMP_MAP,
    BUMP_MAP_MAJOR_VERSION_ZERO,
    BUMP_PATTERN,
)
from commitizen.exceptions import NoPatternMapError


@pytest.fixture
def bump_rule():
    return ConventionalCommitBumpRule()


class TestConventionalCommitBumpRule:
    def test_feat_commit(self, bump_rule):
        assert (
            bump_rule.get_increment("feat: add new feature", False)
            == SemVerIncrement.MINOR
        )
        assert (
            bump_rule.get_increment("feat: add new feature", True)
            == SemVerIncrement.MINOR
        )

    def test_fix_commit(self, bump_rule):
        assert bump_rule.get_increment("fix: fix bug", False) == SemVerIncrement.PATCH
        assert bump_rule.get_increment("fix: fix bug", True) == SemVerIncrement.PATCH

    def test_perf_commit(self, bump_rule):
        assert (
            bump_rule.get_increment("perf: improve performance", False)
            == SemVerIncrement.PATCH
        )
        assert (
            bump_rule.get_increment("perf: improve performance", True)
            == SemVerIncrement.PATCH
        )

    def test_refactor_commit(self, bump_rule):
        assert (
            bump_rule.get_increment("refactor: restructure code", False)
            == SemVerIncrement.PATCH
        )
        assert (
            bump_rule.get_increment("refactor: restructure code", True)
            == SemVerIncrement.PATCH
        )

    def test_breaking_change_with_bang(self, bump_rule):
        assert (
            bump_rule.get_increment("feat!: breaking change", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            bump_rule.get_increment("feat!: breaking change", True)
            == SemVerIncrement.MINOR
        )

    def test_breaking_change_type(self, bump_rule):
        assert (
            bump_rule.get_increment("BREAKING CHANGE: major change", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            bump_rule.get_increment("BREAKING CHANGE: major change", True)
            == SemVerIncrement.MINOR
        )

    def test_commit_with_scope(self, bump_rule):
        assert (
            bump_rule.get_increment("feat(api): add new endpoint", False)
            == SemVerIncrement.MINOR
        )
        assert (
            bump_rule.get_increment("fix(ui): fix button alignment", False)
            == SemVerIncrement.PATCH
        )

    def test_commit_with_complex_scopes(self, bump_rule):
        # Test with multiple word scopes
        assert (
            bump_rule.get_increment("feat(user_management): add user roles", False)
            == SemVerIncrement.MINOR
        )
        assert (
            bump_rule.get_increment("fix(database_connection): handle timeout", False)
            == SemVerIncrement.PATCH
        )

        # Test with nested scopes
        assert (
            bump_rule.get_increment("feat(api/auth): implement OAuth", False)
            == SemVerIncrement.MINOR
        )
        assert (
            bump_rule.get_increment("fix(ui/components): fix dropdown", False)
            == SemVerIncrement.PATCH
        )

        # Test with breaking changes and scopes
        assert (
            bump_rule.get_increment("feat(api)!: remove deprecated endpoints", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            bump_rule.get_increment("feat(api)!: remove deprecated endpoints", True)
            == SemVerIncrement.MINOR
        )

        # Test with BREAKING CHANGE and scopes
        assert (
            bump_rule.get_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", False
            )
            == SemVerIncrement.MAJOR
        )
        assert (
            bump_rule.get_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", True
            )
            == SemVerIncrement.MINOR
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

    def test_breaking_change_with_refactor(self, bump_rule):
        """Test breaking changes with refactor type commit messages."""
        # Breaking change with refactor type
        assert (
            bump_rule.get_increment("refactor!: drop support for Python 2.7", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            bump_rule.get_increment("refactor!: drop support for Python 2.7", True)
            == SemVerIncrement.MINOR
        )

        # Breaking change with refactor type and scope
        assert (
            bump_rule.get_increment(
                "refactor(api)!: remove deprecated endpoints", False
            )
            == SemVerIncrement.MAJOR
        )
        assert (
            bump_rule.get_increment("refactor(api)!: remove deprecated endpoints", True)
            == SemVerIncrement.MINOR
        )

        # Regular refactor (should be SemVerIncrement.PATCH)
        assert (
            bump_rule.get_increment("refactor: improve code structure", False)
            == SemVerIncrement.PATCH
        )
        assert (
            bump_rule.get_increment("refactor: improve code structure", True)
            == SemVerIncrement.PATCH
        )


class TestFindIncrementByCallable:
    @pytest.fixture
    def get_increment(self, bump_rule):
        return lambda x: bump_rule.get_increment(x, False)

    def test_single_commit(self, get_increment):
        commit_messages = ["feat: add new feature"]
        assert (
            find_increment_by_callable(commit_messages, get_increment)
            == SemVerIncrement.MINOR
        )

    def test_multiple_commits(self, get_increment):
        commit_messages = [
            "feat: new feature",
            "fix: bug fix",
            "docs: update readme",
        ]
        assert (
            find_increment_by_callable(commit_messages, get_increment)
            == SemVerIncrement.MINOR
        )

    def test_breaking_change(self, get_increment):
        commit_messages = [
            "feat: new feature",
            "feat!: breaking change",
        ]
        assert (
            find_increment_by_callable(commit_messages, get_increment)
            == SemVerIncrement.MAJOR
        )

    def test_multi_line_commit(self, get_increment):
        commit_messages = [
            "feat: new feature\n\nBREAKING CHANGE: major change",
        ]
        assert (
            find_increment_by_callable(commit_messages, get_increment)
            == SemVerIncrement.MAJOR
        )

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
            == SemVerIncrement.MINOR
        )

    def test_mixed_commit_types(self, get_increment):
        commit_messages = [
            "feat: new feature",
            "fix: bug fix",
            "perf: improve performance",
            "refactor: restructure code",
        ]
        assert (
            find_increment_by_callable(commit_messages, get_increment)
            == SemVerIncrement.MINOR
        )

    def test_commit_with_scope(self, get_increment):
        commit_messages = [
            "feat(api): add new endpoint",
            "fix(ui): fix button alignment",
        ]
        assert (
            find_increment_by_callable(commit_messages, get_increment)
            == SemVerIncrement.MINOR
        )


class TestOldSchoolBumpRule:
    @pytest.fixture
    def bump_pattern(self):
        return r"^.*?\[(.*?)\].*$"

    @pytest.fixture
    def bump_map(self):
        return {
            "SemVerIncrement.MAJOR": SemVerIncrement.MAJOR,
            "SemVerIncrement.MINOR": SemVerIncrement.MINOR,
            "SemVerIncrement.PATCH": SemVerIncrement.PATCH,
        }

    @pytest.fixture
    def bump_map_major_version_zero(self):
        return {
            "SemVerIncrement.MAJOR": SemVerIncrement.MINOR,  # SemVerIncrement.MAJOR becomes SemVerIncrement.MINOR in version zero
            "SemVerIncrement.MINOR": SemVerIncrement.MINOR,
            "SemVerIncrement.PATCH": SemVerIncrement.PATCH,
        }

    @pytest.fixture
    def old_school_rule(self, bump_pattern, bump_map, bump_map_major_version_zero):
        return OldSchoolBumpRule(bump_pattern, bump_map, bump_map_major_version_zero)

    def test_major_version(self, old_school_rule):
        assert (
            old_school_rule.get_increment(
                "feat: add new feature [SemVerIncrement.MAJOR]", False
            )
            == SemVerIncrement.MAJOR
        )
        assert (
            old_school_rule.get_increment("fix: bug fix [SemVerIncrement.MAJOR]", False)
            == SemVerIncrement.MAJOR
        )

    def test_minor_version(self, old_school_rule):
        assert (
            old_school_rule.get_increment(
                "feat: add new feature [SemVerIncrement.MINOR]", False
            )
            == SemVerIncrement.MINOR
        )
        assert (
            old_school_rule.get_increment("fix: bug fix [SemVerIncrement.MINOR]", False)
            == SemVerIncrement.MINOR
        )

    def test_patch_version(self, old_school_rule):
        assert (
            old_school_rule.get_increment(
                "feat: add new feature [SemVerIncrement.PATCH]", False
            )
            == SemVerIncrement.PATCH
        )
        assert (
            old_school_rule.get_increment("fix: bug fix [SemVerIncrement.PATCH]", False)
            == SemVerIncrement.PATCH
        )

    def test_major_version_zero(self, old_school_rule):
        assert (
            old_school_rule.get_increment(
                "feat: add new feature [SemVerIncrement.MAJOR]", True
            )
            == SemVerIncrement.MINOR
        )
        assert (
            old_school_rule.get_increment("fix: bug fix [SemVerIncrement.MAJOR]", True)
            == SemVerIncrement.MINOR
        )

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
            "SemVerIncrement.MAJOR": SemVerIncrement.MAJOR,
            "SemVerIncrement.MINOR": SemVerIncrement.MINOR,
            "SemVerIncrement.PATCH": SemVerIncrement.PATCH,
        }
        rule = OldSchoolBumpRule(pattern, bump_map, bump_map)

        assert (
            rule.get_increment(
                "feat: add new feature [SemVerIncrement.MAJOR] [SemVerIncrement.MINOR]",
                False,
            )
            == SemVerIncrement.MAJOR
        )
        assert (
            rule.get_increment(
                "fix: bug fix [SemVerIncrement.MINOR] [SemVerIncrement.PATCH]", False
            )
            == SemVerIncrement.MINOR
        )

    def test_with_find_increment_by_callable(self, old_school_rule):
        commit_messages = [
            "feat: add new feature [SemVerIncrement.MAJOR]",
            "fix: bug fix [SemVerIncrement.PATCH]",
            "docs: update readme [SemVerIncrement.MINOR]",
        ]
        assert (
            find_increment_by_callable(
                commit_messages, lambda x: old_school_rule.get_increment(x, False)
            )
            == SemVerIncrement.MAJOR
        )

    def test_flexible_bump_map(self, old_school_rule):
        """Test that _find_highest_increment is used correctly in bump map processing."""
        # Test with multiple matching patterns
        pattern = r"^((?P<major>major)|(?P<minor>minor)|(?P<patch>patch))(?P<scope>\(.+\))?(?P<bang>!)?:"
        bump_map = {
            "major": SemVerIncrement.MAJOR,
            "bang": SemVerIncrement.MAJOR,
            "minor": SemVerIncrement.MINOR,
            "patch": SemVerIncrement.PATCH,
        }
        bump_map_major_version_zero = {
            "major": SemVerIncrement.MINOR,
            "bang": SemVerIncrement.MINOR,
            "minor": SemVerIncrement.MINOR,
            "patch": SemVerIncrement.PATCH,
        }
        rule = OldSchoolBumpRule(pattern, bump_map, bump_map_major_version_zero)

        # Test with multiple version tags
        assert (
            rule.get_increment("major!: drop support for Python 2.7", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            rule.get_increment("major!: drop support for Python 2.7", True)
            == SemVerIncrement.MINOR
        )
        assert (
            rule.get_increment("major: drop support for Python 2.7", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            rule.get_increment("major: drop support for Python 2.7", True)
            == SemVerIncrement.MINOR
        )
        assert (
            rule.get_increment("patch!: drop support for Python 2.7", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            rule.get_increment("patch!: drop support for Python 2.7", True)
            == SemVerIncrement.MINOR
        )
        assert (
            rule.get_increment("patch: drop support for Python 2.7", False)
            == SemVerIncrement.PATCH
        )
        assert (
            rule.get_increment("patch: drop support for Python 2.7", True)
            == SemVerIncrement.PATCH
        )
        assert (
            rule.get_increment("minor: add new feature", False) == SemVerIncrement.MINOR
        )
        assert (
            rule.get_increment("minor: add new feature", True) == SemVerIncrement.MINOR
        )
        assert rule.get_increment("patch: fix bug", False) == SemVerIncrement.PATCH
        assert rule.get_increment("patch: fix bug", True) == SemVerIncrement.PATCH


class TestOldSchoolBumpRuleWithDefault:
    @pytest.fixture
    def old_school_rule(self):
        return OldSchoolBumpRule(BUMP_PATTERN, BUMP_MAP, BUMP_MAP_MAJOR_VERSION_ZERO)

    def test_breaking_change_with_bang(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat!: breaking change", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            old_school_rule.get_increment("fix!: breaking change", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            old_school_rule.get_increment("feat!: breaking change", True)
            == SemVerIncrement.MINOR
        )
        assert (
            old_school_rule.get_increment("fix!: breaking change", True)
            == SemVerIncrement.MINOR
        )

    def test_breaking_change_type(self, old_school_rule):
        assert (
            old_school_rule.get_increment("BREAKING CHANGE: major change", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            old_school_rule.get_increment("BREAKING-CHANGE: major change", False)
            == SemVerIncrement.MAJOR
        )
        assert (
            old_school_rule.get_increment("BREAKING CHANGE: major change", True)
            == SemVerIncrement.MINOR
        )
        assert (
            old_school_rule.get_increment("BREAKING-CHANGE: major change", True)
            == SemVerIncrement.MINOR
        )

    def test_feat_commit(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat: add new feature", False)
            == SemVerIncrement.MINOR
        )
        assert (
            old_school_rule.get_increment("feat: add new feature", True)
            == SemVerIncrement.MINOR
        )

    def test_fix_commit(self, old_school_rule):
        assert (
            old_school_rule.get_increment("fix: fix bug", False)
            == SemVerIncrement.PATCH
        )
        assert (
            old_school_rule.get_increment("fix: fix bug", True) == SemVerIncrement.PATCH
        )

    def test_refactor_commit(self, old_school_rule):
        assert (
            old_school_rule.get_increment("refactor: restructure code", False)
            == SemVerIncrement.PATCH
        )
        assert (
            old_school_rule.get_increment("refactor: restructure code", True)
            == SemVerIncrement.PATCH
        )

    def test_perf_commit(self, old_school_rule):
        assert (
            old_school_rule.get_increment("perf: improve performance", False)
            == SemVerIncrement.PATCH
        )
        assert (
            old_school_rule.get_increment("perf: improve performance", True)
            == SemVerIncrement.PATCH
        )

    def test_commit_with_scope(self, old_school_rule):
        assert (
            old_school_rule.get_increment("feat(api): add new endpoint", False)
            == SemVerIncrement.MINOR
        )
        assert (
            old_school_rule.get_increment("fix(ui): fix button alignment", False)
            == SemVerIncrement.PATCH
        )
        assert (
            old_school_rule.get_increment("refactor(core): restructure", False)
            == SemVerIncrement.PATCH
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
            == SemVerIncrement.MAJOR
        )


def test_find_highest_increment():
    """Test the _find_highest_increment function."""
    # Test with single increment
    assert _find_highest_increment([SemVerIncrement.MAJOR]) == SemVerIncrement.MAJOR
    assert _find_highest_increment([SemVerIncrement.MINOR]) == SemVerIncrement.MINOR
    assert _find_highest_increment([SemVerIncrement.PATCH]) == SemVerIncrement.PATCH

    # Test with multiple increments
    assert (
        _find_highest_increment(
            [SemVerIncrement.PATCH, SemVerIncrement.MINOR, SemVerIncrement.MAJOR]
        )
        == SemVerIncrement.MAJOR
    )
    assert (
        _find_highest_increment([SemVerIncrement.PATCH, SemVerIncrement.MINOR])
        == SemVerIncrement.MINOR
    )
    assert (
        _find_highest_increment([SemVerIncrement.PATCH, SemVerIncrement.PATCH])
        == SemVerIncrement.PATCH
    )

    # Test with None values
    assert (
        _find_highest_increment([None, SemVerIncrement.PATCH]) == SemVerIncrement.PATCH
    )
    assert _find_highest_increment([None, None]) is None
    assert _find_highest_increment([]) is None

    # Test with mixed values
    assert (
        _find_highest_increment(
            [None, SemVerIncrement.PATCH, SemVerIncrement.MINOR, SemVerIncrement.MAJOR]
        )
        == SemVerIncrement.MAJOR
    )
    assert (
        _find_highest_increment([None, SemVerIncrement.PATCH, SemVerIncrement.MINOR])
        == SemVerIncrement.MINOR
    )
    assert (
        _find_highest_increment([None, SemVerIncrement.PATCH]) == SemVerIncrement.PATCH
    )

    # Test with empty iterator
    assert _find_highest_increment(iter([])) is None

    # Test with generator expression
    assert (
        _find_highest_increment(
            x
            for x in [
                SemVerIncrement.PATCH,
                SemVerIncrement.MINOR,
                SemVerIncrement.MAJOR,
            ]
        )
        == SemVerIncrement.MAJOR
    )
    assert (
        _find_highest_increment(
            x for x in [None, SemVerIncrement.PATCH, SemVerIncrement.MINOR]
        )
        == SemVerIncrement.MINOR
    )
