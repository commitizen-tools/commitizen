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
        # ``bump_map_major_version_zero`` is optional at construction time.
        # An empty map is allowed; it only triggers ``NoPatternMapError`` when
        # ``extract_increment`` is called with ``major_version_zero=True``.
        rule = CustomBumpRule(bump_pattern, bump_map, {})
        # Non-zero mode keeps working with the regular bump_map.
        assert (
            rule.extract_increment("feat: x [MAJOR]", False) == VersionIncrement.MAJOR
        )
        # Zero mode raises because the MVZ map is empty.
        with pytest.raises(NoPatternMapError):
            rule.extract_increment("feat: x [MAJOR]", True)

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


class TestCustomBumpRuleWithoutMajorVersionZeroMap:
    """Backward-compat: legacy plugins may only define ``bump_pattern`` and
    ``bump_map`` and never set ``bump_map_major_version_zero``. The rule must
    still construct cleanly and only fail when ``major_version_zero`` is True.
    Mirrors master's lazy validation in ``commands/bump.py::_find_increment``.
    """

    @pytest.fixture
    def rule(self):
        return CustomBumpRule(
            BUMP_PATTERN,
            VersionIncrement.safe_cast_dict(BUMP_MAP),
            # bump_map_major_version_zero intentionally omitted
        )

    def test_construct_without_mvz_map(self, rule):
        assert rule.bump_map_major_version_zero is None

    def test_extract_with_major_version_zero_false_works(self, rule):
        assert (
            rule.extract_increment("feat: add new feature", False)
            == VersionIncrement.MINOR
        )
        assert rule.extract_increment("fix: bug fix", False) == VersionIncrement.PATCH

    def test_extract_with_major_version_zero_true_raises(self, rule):
        with pytest.raises(NoPatternMapError):
            rule.extract_increment("feat: add new feature", True)


class TestCustomBumpRuleFallbackOrder:
    """The legacy fallback path returns the FIRST matching pattern. Iteration
    order of the bump_map matters and must be preserved.
    """

    def test_first_matching_pattern_wins(self):
        # Both r"^.+!$" and r"^feat" match "feat!"; the first one in insertion
        # order should win. With this ordering the result is MAJOR.
        rule_major_first = CustomBumpRule(
            r"^((BREAKING[\-\ ]CHANGE|\w+)(\(.+\))?!?):",
            {
                r"^.+!$": VersionIncrement.MAJOR,
                r"^feat": VersionIncrement.MINOR,
            },
        )
        assert (
            rule_major_first.extract_increment("feat!: breaking", False)
            == VersionIncrement.MAJOR
        )

        # Reversed insertion order: now MINOR wins because r"^feat" is tried first.
        rule_minor_first = CustomBumpRule(
            r"^((BREAKING[\-\ ]CHANGE|\w+)(\(.+\))?!?):",
            {
                r"^feat": VersionIncrement.MINOR,
                r"^.+!$": VersionIncrement.MAJOR,
            },
        )
        assert (
            rule_minor_first.extract_increment("feat!: breaking", False)
            == VersionIncrement.MINOR
        )


class TestBaseCommitizenBumpRuleProperty:
    """Verifies the cached_property in ``commitizen.cz.base.BaseCommitizen``
    that lazily resolves a ``BumpRule`` from class-level ``bump_pattern`` /
    ``bump_map`` / ``bump_map_major_version_zero`` attributes — used by
    third-party plugins.
    """

    @pytest.fixture
    def config(self):
        from commitizen.config import BaseConfig

        c = BaseConfig()
        c.settings.update({"name": "cz_legacy_plugin"})
        return c

    def test_plugin_with_only_bump_pattern_and_bump_map_works(self, config):
        """Master-compatible: a plugin that omits ``bump_map_major_version_zero``
        must still produce a working rule when ``major_version_zero=False``."""
        from commitizen.cz.base import BaseCommitizen

        class _LegacyCz(BaseCommitizen):
            bump_pattern = BUMP_PATTERN
            bump_map = BUMP_MAP
            # bump_map_major_version_zero deliberately not set

            def questions(self):
                return []

            def message(self, answers):
                return ""

            def example(self):
                return ""

            def schema(self):
                return ""

            def schema_pattern(self):
                return ""

            def info(self):
                return ""

        rule = _LegacyCz(config).bump_rule
        assert rule.extract_increment("feat: x", False) == VersionIncrement.MINOR
        # And only fails when major_version_zero is actually required.
        with pytest.raises(NoPatternMapError):
            rule.extract_increment("feat: x", True)

    def test_plugin_without_bump_pattern_raises(self, config):
        from commitizen.cz.base import BaseCommitizen

        class _BrokenCz(BaseCommitizen):
            bump_pattern = None
            bump_map = BUMP_MAP

            def questions(self):
                return []

            def message(self, answers):
                return ""

            def example(self):
                return ""

            def schema(self):
                return ""

            def schema_pattern(self):
                return ""

            def info(self):
                return ""

        with pytest.raises(NoPatternMapError):
            _BrokenCz(config).bump_rule
