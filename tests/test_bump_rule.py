import pytest

from commitizen.bump_rule import (
    ConventionalCommitBumpRule,
    CustomBumpRule,
    VersionIncrement,
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
            bump_rule.extract_increment("feat: add new feature", False)
            == VersionIncrement.MINOR
        )
        assert (
            bump_rule.extract_increment("feat: add new feature", True)
            == VersionIncrement.MINOR
        )

    def test_fix_commit(self, bump_rule):
        assert (
            bump_rule.extract_increment("fix: fix bug", False) == VersionIncrement.PATCH
        )
        assert (
            bump_rule.extract_increment("fix: fix bug", True) == VersionIncrement.PATCH
        )

    def test_perf_commit(self, bump_rule):
        assert (
            bump_rule.extract_increment("perf: improve performance", False)
            == VersionIncrement.PATCH
        )
        assert (
            bump_rule.extract_increment("perf: improve performance", True)
            == VersionIncrement.PATCH
        )

    def test_refactor_commit(self, bump_rule):
        assert (
            bump_rule.extract_increment("refactor: restructure code", False)
            == VersionIncrement.PATCH
        )
        assert (
            bump_rule.extract_increment("refactor: restructure code", True)
            == VersionIncrement.PATCH
        )

    def test_breaking_change_with_bang(self, bump_rule):
        assert (
            bump_rule.extract_increment("feat!: breaking change", False)
            == VersionIncrement.MAJOR
        )
        assert (
            bump_rule.extract_increment("feat!: breaking change", True)
            == VersionIncrement.MINOR
        )

    def test_breaking_change_type(self, bump_rule):
        assert (
            bump_rule.extract_increment("BREAKING CHANGE: major change", False)
            == VersionIncrement.MAJOR
        )
        assert (
            bump_rule.extract_increment("BREAKING CHANGE: major change", True)
            == VersionIncrement.MINOR
        )

    def test_commit_with_scope(self, bump_rule):
        assert (
            bump_rule.extract_increment("feat(api): add new endpoint", False)
            == VersionIncrement.MINOR
        )
        assert (
            bump_rule.extract_increment("fix(ui): fix button alignment", False)
            == VersionIncrement.PATCH
        )

    def test_commit_with_complex_scopes(self, bump_rule):
        # Test with multiple word scopes
        assert (
            bump_rule.extract_increment("feat(user_management): add user roles", False)
            == VersionIncrement.MINOR
        )
        assert (
            bump_rule.extract_increment(
                "fix(database_connection): handle timeout", False
            )
            == VersionIncrement.PATCH
        )

        # Test with nested scopes
        assert (
            bump_rule.extract_increment("feat(api/auth): implement OAuth", False)
            == VersionIncrement.MINOR
        )
        assert (
            bump_rule.extract_increment("fix(ui/components): fix dropdown", False)
            == VersionIncrement.PATCH
        )

        # Test with breaking changes and scopes
        assert (
            bump_rule.extract_increment(
                "feat(api)!: remove deprecated endpoints", False
            )
            == VersionIncrement.MAJOR
        )
        assert (
            bump_rule.extract_increment("feat(api)!: remove deprecated endpoints", True)
            == VersionIncrement.MINOR
        )

        # Test with BREAKING CHANGE and scopes
        assert (
            bump_rule.extract_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", False
            )
            == VersionIncrement.MAJOR
        )
        assert (
            bump_rule.extract_increment(
                "BREAKING CHANGE(api): remove deprecated endpoints", True
            )
            == VersionIncrement.MINOR
        )

    def test_invalid_commit_message(self, bump_rule):
        assert (
            bump_rule.extract_increment("invalid commit message", False)
            == VersionIncrement.NONE
        )
        assert bump_rule.extract_increment("", False) == VersionIncrement.NONE
        assert bump_rule.extract_increment("feat", False) == VersionIncrement.NONE

    def test_other_commit_types(self, bump_rule):
        # These commit types should not trigger any version bump
        assert (
            bump_rule.extract_increment("docs: update documentation", False)
            == VersionIncrement.NONE
        )
        assert (
            bump_rule.extract_increment("style: format code", False)
            == VersionIncrement.NONE
        )
        assert (
            bump_rule.extract_increment("test: add unit tests", False)
            == VersionIncrement.NONE
        )
        assert (
            bump_rule.extract_increment("build: update build config", False)
            == VersionIncrement.NONE
        )
        assert (
            bump_rule.extract_increment("ci: update CI pipeline", False)
            == VersionIncrement.NONE
        )

    def test_breaking_change_with_refactor(self, bump_rule):
        """Test breaking changes with refactor type commit messages."""
        # Breaking change with refactor type
        assert (
            bump_rule.extract_increment("refactor!: drop support for Python 2.7", False)
            == VersionIncrement.MAJOR
        )
        assert (
            bump_rule.extract_increment("refactor!: drop support for Python 2.7", True)
            == VersionIncrement.MINOR
        )

        # Breaking change with refactor type and scope
        assert (
            bump_rule.extract_increment(
                "refactor(api)!: remove deprecated endpoints", False
            )
            == VersionIncrement.MAJOR
        )
        assert (
            bump_rule.extract_increment(
                "refactor(api)!: remove deprecated endpoints", True
            )
            == VersionIncrement.MINOR
        )

        # Regular refactor (should be VersionIncrement.PATCH)
        assert (
            bump_rule.extract_increment("refactor: improve code structure", False)
            == VersionIncrement.PATCH
        )
        assert (
            bump_rule.extract_increment("refactor: improve code structure", True)
            == VersionIncrement.PATCH
        )


class TestFindIncrementByCallable:
    @pytest.fixture
    def extract_increment(self, bump_rule):
        return lambda x: bump_rule.extract_increment(x, False)

    def test_single_commit(self, extract_increment):
        commit_messages = ["feat: add new feature"]
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.MINOR
        )

    def test_multiple_commits(self, extract_increment):
        commit_messages = [
            "feat: new feature",
            "fix: bug fix",
            "docs: update readme",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.MINOR
        )

    def test_breaking_change(self, extract_increment):
        commit_messages = [
            "feat: new feature",
            "feat!: breaking change",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.MAJOR
        )

    def test_multi_line_commit(self, extract_increment):
        commit_messages = [
            "feat: new feature\n\nBREAKING CHANGE: major change",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.MAJOR
        )

    def test_no_increment_needed(self, extract_increment):
        commit_messages = [
            "docs: update documentation",
            "style: format code",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.NONE
        )

    def test_empty_commits(self, extract_increment):
        commit_messages = []
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.NONE
        )

    def test_major_version_zero(self):
        bump_rule = ConventionalCommitBumpRule()

        commit_messages = [
            "feat!: breaking change",
            "BREAKING CHANGE: major change",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(
                commit_messages, lambda x: bump_rule.extract_increment(x, True)
            )
            == VersionIncrement.MINOR
        )

    def test_mixed_commit_types(self, extract_increment):
        commit_messages = [
            "feat: new feature",
            "fix: bug fix",
            "perf: improve performance",
            "refactor: restructure code",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.MINOR
        )

    def test_commit_with_scope(self, extract_increment):
        commit_messages = [
            "feat(api): add new endpoint",
            "fix(ui): fix button alignment",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(commit_messages, extract_increment)
            == VersionIncrement.MINOR
        )


class TestCustomBumpRule:
    @pytest.fixture
    def bump_pattern(self):
        return r"^.*?\[(.*?)\].*$"

    @pytest.fixture
    def bump_map(self):
        return {
            "MAJOR": VersionIncrement.MAJOR,
            "MINOR": VersionIncrement.MINOR,
            "PATCH": VersionIncrement.PATCH,
        }

    @pytest.fixture
    def bump_map_major_version_zero(self):
        return {
            "MAJOR": VersionIncrement.MINOR,  # VersionIncrement.MAJOR becomes VersionIncrement.MINOR in version zero
            "MINOR": VersionIncrement.MINOR,
            "PATCH": VersionIncrement.PATCH,
        }

    @pytest.fixture
    def custom_bump_rule(self, bump_pattern, bump_map, bump_map_major_version_zero):
        return CustomBumpRule(bump_pattern, bump_map, bump_map_major_version_zero)

    def test_major_version(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat: add new feature [MAJOR]", False)
            == VersionIncrement.MAJOR
        )
        assert (
            custom_bump_rule.extract_increment("fix: bug fix [MAJOR]", False)
            == VersionIncrement.MAJOR
        )

    def test_minor_version(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat: add new feature [MINOR]", False)
            == VersionIncrement.MINOR
        )
        assert (
            custom_bump_rule.extract_increment("fix: bug fix [MINOR]", False)
            == VersionIncrement.MINOR
        )

    def test_patch_version(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat: add new feature [PATCH]", False)
            == VersionIncrement.PATCH
        )
        assert (
            custom_bump_rule.extract_increment("fix: bug fix [PATCH]", False)
            == VersionIncrement.PATCH
        )

    def test_major_version_zero(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat: add new feature [MAJOR]", True)
            == VersionIncrement.MINOR
        )
        assert (
            custom_bump_rule.extract_increment("fix: bug fix [MAJOR]", True)
            == VersionIncrement.MINOR
        )

    def test_no_match(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat: add new feature", False)
            == VersionIncrement.NONE
        )
        assert (
            custom_bump_rule.extract_increment("fix: bug fix", False)
            == VersionIncrement.NONE
        )

    def test_invalid_pattern(self, bump_map, bump_map_major_version_zero):
        with pytest.raises(NoPatternMapError):
            CustomBumpRule("", bump_map, bump_map_major_version_zero)

    def test_invalid_bump_map(self, bump_pattern):
        with pytest.raises(NoPatternMapError):
            CustomBumpRule(bump_pattern, {}, {})

    def test_invalid_bump_map_major_version_zero(self, bump_pattern, bump_map):
        with pytest.raises(NoPatternMapError):
            CustomBumpRule(bump_pattern, bump_map, {})

    def test_all_invalid(self):
        with pytest.raises(NoPatternMapError):
            CustomBumpRule("", {}, {})

    def test_none_values(self):
        with pytest.raises(NoPatternMapError):
            CustomBumpRule(None, {}, {})

    def test_empty_pattern_with_valid_maps(self, bump_map, bump_map_major_version_zero):
        with pytest.raises(NoPatternMapError):
            CustomBumpRule("", bump_map, bump_map_major_version_zero)

    def test_empty_maps_with_valid_pattern(self, bump_pattern):
        with pytest.raises(NoPatternMapError):
            CustomBumpRule(bump_pattern, {}, {})

    def test_complex_pattern(self):
        pattern = r"^.*?\[(.*?)\].*?\[(.*?)\].*$"
        bump_map = {
            "MAJOR": VersionIncrement.MAJOR,
            "MINOR": VersionIncrement.MINOR,
            "PATCH": VersionIncrement.PATCH,
        }
        rule = CustomBumpRule(pattern, bump_map, bump_map)

        assert (
            rule.extract_increment(
                "feat: add new feature [MAJOR] [MINOR]",
                False,
            )
            == VersionIncrement.MAJOR
        )
        assert (
            rule.extract_increment("fix: bug fix [MINOR] [PATCH]", False)
            == VersionIncrement.MINOR
        )

    def test_with_find_increment_by_callable(self, custom_bump_rule):
        commit_messages = [
            "feat: add new feature [MAJOR]",
            "fix: bug fix [PATCH]",
            "docs: update readme [MINOR]",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(
                commit_messages, lambda x: custom_bump_rule.extract_increment(x, False)
            )
            == VersionIncrement.MAJOR
        )

    def test_flexible_bump_map(self, custom_bump_rule):
        """Test that _find_highest_increment is used correctly in bump map processing."""
        # Test with multiple matching patterns
        pattern = r"^((?P<major>major)|(?P<minor>minor)|(?P<patch>patch))(?P<scope>\(.+\))?(?P<bang>!)?:"
        bump_map = {
            "major": VersionIncrement.MAJOR,
            "bang": VersionIncrement.MAJOR,
            "minor": VersionIncrement.MINOR,
            "patch": VersionIncrement.PATCH,
        }
        bump_map_major_version_zero = {
            "major": VersionIncrement.MINOR,
            "bang": VersionIncrement.MINOR,
            "minor": VersionIncrement.MINOR,
            "patch": VersionIncrement.PATCH,
        }
        rule = CustomBumpRule(pattern, bump_map, bump_map_major_version_zero)

        # Test with multiple version tags
        assert (
            rule.extract_increment("major!: drop support for Python 2.7", False)
            == VersionIncrement.MAJOR
        )
        assert (
            rule.extract_increment("major!: drop support for Python 2.7", True)
            == VersionIncrement.MINOR
        )
        assert (
            rule.extract_increment("major: drop support for Python 2.7", False)
            == VersionIncrement.MAJOR
        )
        assert (
            rule.extract_increment("major: drop support for Python 2.7", True)
            == VersionIncrement.MINOR
        )
        assert (
            rule.extract_increment("patch!: drop support for Python 2.7", False)
            == VersionIncrement.MAJOR
        )
        assert (
            rule.extract_increment("patch!: drop support for Python 2.7", True)
            == VersionIncrement.MINOR
        )
        assert (
            rule.extract_increment("patch: drop support for Python 2.7", False)
            == VersionIncrement.PATCH
        )
        assert (
            rule.extract_increment("patch: drop support for Python 2.7", True)
            == VersionIncrement.PATCH
        )
        assert (
            rule.extract_increment("minor: add new feature", False)
            == VersionIncrement.MINOR
        )
        assert (
            rule.extract_increment("minor: add new feature", True)
            == VersionIncrement.MINOR
        )
        assert rule.extract_increment("patch: fix bug", False) == VersionIncrement.PATCH
        assert rule.extract_increment("patch: fix bug", True) == VersionIncrement.PATCH


class TestCustomBumpRuleWithDefault:
    @pytest.fixture
    def custom_bump_rule(self):
        return CustomBumpRule(
            BUMP_PATTERN,
            VersionIncrement.safe_cast_dict(BUMP_MAP),
            VersionIncrement.safe_cast_dict(BUMP_MAP_MAJOR_VERSION_ZERO),
        )

    def test_breaking_change_with_bang(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat!: breaking change", False)
            == VersionIncrement.MAJOR
        )
        assert (
            custom_bump_rule.extract_increment("fix!: breaking change", False)
            == VersionIncrement.MAJOR
        )
        assert (
            custom_bump_rule.extract_increment("feat!: breaking change", True)
            == VersionIncrement.MINOR
        )
        assert (
            custom_bump_rule.extract_increment("fix!: breaking change", True)
            == VersionIncrement.MINOR
        )

    def test_breaking_change_type(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("BREAKING CHANGE: major change", False)
            == VersionIncrement.MAJOR
        )
        assert (
            custom_bump_rule.extract_increment("BREAKING-CHANGE: major change", False)
            == VersionIncrement.MAJOR
        )
        assert (
            custom_bump_rule.extract_increment("BREAKING CHANGE: major change", True)
            == VersionIncrement.MINOR
        )
        assert (
            custom_bump_rule.extract_increment("BREAKING-CHANGE: major change", True)
            == VersionIncrement.MINOR
        )

    def test_feat_commit(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat: add new feature", False)
            == VersionIncrement.MINOR
        )
        assert (
            custom_bump_rule.extract_increment("feat: add new feature", True)
            == VersionIncrement.MINOR
        )

    def test_fix_commit(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("fix: fix bug", False)
            == VersionIncrement.PATCH
        )
        assert (
            custom_bump_rule.extract_increment("fix: fix bug", True)
            == VersionIncrement.PATCH
        )

    def test_refactor_commit(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("refactor: restructure code", False)
            == VersionIncrement.PATCH
        )
        assert (
            custom_bump_rule.extract_increment("refactor: restructure code", True)
            == VersionIncrement.PATCH
        )

    def test_perf_commit(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("perf: improve performance", False)
            == VersionIncrement.PATCH
        )
        assert (
            custom_bump_rule.extract_increment("perf: improve performance", True)
            == VersionIncrement.PATCH
        )

    def test_commit_with_scope(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("feat(api): add new endpoint", False)
            == VersionIncrement.MINOR
        )
        assert (
            custom_bump_rule.extract_increment("fix(ui): fix button alignment", False)
            == VersionIncrement.PATCH
        )
        assert (
            custom_bump_rule.extract_increment("refactor(core): restructure", False)
            == VersionIncrement.PATCH
        )

    def test_no_match(self, custom_bump_rule):
        assert (
            custom_bump_rule.extract_increment("docs: update documentation", False)
            == VersionIncrement.NONE
        )
        assert (
            custom_bump_rule.extract_increment("style: format code", False)
            == VersionIncrement.NONE
        )
        assert (
            custom_bump_rule.extract_increment("test: add unit tests", False)
            == VersionIncrement.NONE
        )
        assert (
            custom_bump_rule.extract_increment("build: update build config", False)
            == VersionIncrement.NONE
        )
        assert (
            custom_bump_rule.extract_increment("ci: update CI pipeline", False)
            == VersionIncrement.NONE
        )

    def test_with_find_increment_by_callable(self, custom_bump_rule):
        commit_messages = [
            "feat!: breaking change",
            "fix: bug fix",
            "perf: improve performance",
        ]
        assert (
            VersionIncrement.get_highest_by_messages(
                commit_messages, lambda x: custom_bump_rule.extract_increment(x, False)
            )
            == VersionIncrement.MAJOR
        )


class TestSafeCast:
    def test_safe_cast_valid_strings(self):
        assert VersionIncrement.safe_cast("MAJOR") == VersionIncrement.MAJOR
        assert VersionIncrement.safe_cast("MINOR") == VersionIncrement.MINOR
        assert VersionIncrement.safe_cast("PATCH") == VersionIncrement.PATCH

    def test_safe_cast_invalid_strings(self):
        assert VersionIncrement.safe_cast("invalid") == VersionIncrement.NONE
        assert (
            VersionIncrement.safe_cast("major") == VersionIncrement.NONE
        )  # case sensitive
        assert VersionIncrement.safe_cast("") == VersionIncrement.NONE

    def test_safe_cast_non_string_values(self):
        assert VersionIncrement.safe_cast(None) == VersionIncrement.NONE
        assert VersionIncrement.safe_cast(1) == VersionIncrement.NONE
        assert VersionIncrement.safe_cast(True) == VersionIncrement.NONE
        assert VersionIncrement.safe_cast([]) == VersionIncrement.NONE
        assert VersionIncrement.safe_cast({}) == VersionIncrement.NONE
        assert (
            VersionIncrement.safe_cast(VersionIncrement.MAJOR) == VersionIncrement.NONE
        )  # enum value itself
