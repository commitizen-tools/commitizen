"""Tests for the incremental_build function in commitizen.changelog module."""

from commitizen.changelog import Metadata, incremental_build


class TestIncrementalBuild:
    """Test cases for the incremental_build function."""

    def test_basic_replacement_of_unreleased_section(self):
        """Test basic functionality of replacing unreleased section with new content."""
        lines = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        metadata = Metadata(
            unreleased_start=2,
            unreleased_end=6,
            latest_version="1.0.0",
            latest_version_position=7,
        )

        new_content = "## Unreleased\n\n### Added\n- Another new feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- Another new feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        assert result == expected

    def test_replacement_when_latest_version_position_is_none(self):
        """Test replacement when latest_version_position is None (append to end)."""
        lines = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
        ]

        metadata = Metadata(
            unreleased_start=2,
            unreleased_end=5,
            latest_version=None,
            latest_version_position=None,
        )

        new_content = "## Unreleased\n\n### Added\n- Another new feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- Another new feature",
        ]

        assert result == expected

    def test_replacement_when_latest_version_position_after_unreleased_end(self):
        """Test replacement when latest_version_position is after unreleased_end."""
        lines = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        metadata = Metadata(
            unreleased_start=2,
            unreleased_end=5,
            latest_version="1.0.0",
            latest_version_position=7,
        )

        new_content = "## Unreleased\n\n### Added\n- Another new feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "",
            "## Unreleased\n\n### Added\n- Another new feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        assert result == expected

    def test_replacement_when_latest_version_position_before_unreleased_end(self):
        """Test replacement when latest_version_position is before unreleased_end."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
        ]

        metadata = Metadata(
            unreleased_start=7,
            unreleased_end=10,
            latest_version="1.0.0",
            latest_version_position=2,
        )

        new_content = "## Unreleased\n\n### Added\n- Another new feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- Another new feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
            "",
            "- New feature",
        ]

        assert result == expected

    def test_no_unreleased_section_append_to_end(self):
        """Test appending new content when no unreleased section exists."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        metadata = Metadata(
            unreleased_start=None,
            unreleased_end=None,
            latest_version=None,
            latest_version_position=None,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
            "\n",
            "## Unreleased\n\n### Added\n- New feature",
        ]

        assert result == expected

    def test_no_unreleased_section_with_latest_version_position(self):
        """Test inserting new content at latest_version_position when no unreleased section."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        metadata = Metadata(
            unreleased_start=None,
            unreleased_end=None,
            latest_version="1.0.0",
            latest_version_position=2,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- New feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        assert result == expected

    def test_empty_lines_list(self):
        """Test behavior with empty lines list."""
        lines = []

        metadata = Metadata(
            unreleased_start=None,
            unreleased_end=None,
            latest_version=None,
            latest_version_position=None,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "## Unreleased\n\n### Added\n- New feature",
        ]

        assert result == expected

    def test_single_line_unreleased_section(self):
        """Test replacement of single line unreleased section."""
        lines = [
            "# Changelog",
            "## Unreleased",
            "## 1.0.0 (2023-01-01)",
        ]

        metadata = Metadata(
            unreleased_start=1,
            unreleased_end=1,
            latest_version="1.0.0",
            latest_version_position=2,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
        ]

        assert result == expected

    def test_unreleased_section_at_end_of_file(self):
        """Test replacement when unreleased section is at the end of file."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
        ]

        metadata = Metadata(
            unreleased_start=7,
            unreleased_end=10,
            latest_version="1.0.0",
            latest_version_position=2,
        )

        new_content = "## Unreleased\n\n### Added\n- Another new feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- Another new feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
            "",
            "- New feature",
        ]

        assert result == expected

    def test_blank_line_handling_when_appending(self):
        """Test that blank line is added when appending to non-empty content."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
        ]

        metadata = Metadata(
            unreleased_start=None,
            unreleased_end=None,
            latest_version=None,
            latest_version_position=None,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "\n",
            "## Unreleased\n\n### Added\n- New feature",
        ]

        assert result == expected

    def test_no_blank_line_when_content_ends_with_blank_line(self):
        """Test that no extra blank line is added when content already ends with blank line."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
        ]

        metadata = Metadata(
            unreleased_start=None,
            unreleased_end=None,
            latest_version=None,
            latest_version_position=None,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "## Unreleased\n\n### Added\n- New feature",
        ]

        assert result == expected

    def test_empty_new_content(self):
        """Test behavior with empty new content."""
        lines = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
            "",
            "## 1.0.0 (2023-01-01)",
        ]

        metadata = Metadata(
            unreleased_start=2,
            unreleased_end=5,
            latest_version="1.0.0",
            latest_version_position=7,
        )

        new_content = ""

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "",
            "",
            "\n",
            "## 1.0.0 (2023-01-01)",
        ]

        assert result == expected

    def test_multiline_new_content(self):
        """Test behavior with multiline new content."""
        lines = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
            "",
            "## 1.0.0 (2023-01-01)",
        ]

        metadata = Metadata(
            unreleased_start=2,
            unreleased_end=5,
            latest_version="1.0.0",
            latest_version_position=7,
        )

        new_content = "## Unreleased\n\n### Added\n- Feature 1\n- Feature 2\n\n### Fixed\n- Bug fix"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "",
            "## Unreleased\n\n### Added\n- Feature 1\n- Feature 2\n\n### Fixed\n- Bug fix",
            "\n",
            "## 1.0.0 (2023-01-01)",
        ]

        assert result == expected

    def test_metadata_with_none_values(self):
        """Test behavior when metadata has None values for unreleased positions."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        metadata = Metadata(
            unreleased_start=None,
            unreleased_end=None,
            latest_version="1.0.0",
            latest_version_position=2,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- New feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        assert result == expected

    def test_skip_behavior_during_unreleased_section(self):
        """Test that lines are properly skipped during unreleased section processing."""
        lines = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- Old feature 1",
            "- Old feature 2",
            "",
            "### Fixed",
            "- Old bug fix",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        metadata = Metadata(
            unreleased_start=2,
            unreleased_end=9,
            latest_version="1.0.0",
            latest_version_position=11,
        )

        new_content = "## Unreleased\n\n### Added\n- New feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "",
            "## Unreleased\n\n### Added\n- New feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
        ]

        assert result == expected

    def test_latest_version_position_at_unreleased_end(self):
        """Test behavior when latest_version_position equals unreleased_end."""
        lines = [
            "# Changelog",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
            "",
            "## 1.0.0 (2023-01-01)",
        ]

        metadata = Metadata(
            unreleased_start=2,
            unreleased_end=5,
            latest_version="1.0.0",
            latest_version_position=5,
        )

        new_content = "## Unreleased\n\n### Added\n- Another new feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- Another new feature",
            "\n",
            "- New feature",
            "",
            "## 1.0.0 (2023-01-01)",
        ]

        assert result == expected

    def test_latest_version_position_before_unreleased_start(self):
        """Test behavior when latest_version_position is before unreleased_start."""
        lines = [
            "# Changelog",
            "",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
            "",
            "## Unreleased",
            "",
            "### Added",
            "- New feature",
        ]

        metadata = Metadata(
            unreleased_start=7,
            unreleased_end=9,
            latest_version="1.0.0",
            latest_version_position=2,
        )

        new_content = "## Unreleased\n\n### Added\n- Another new feature"

        result = incremental_build(new_content, lines, metadata)

        expected = [
            "# Changelog",
            "",
            "## Unreleased\n\n### Added\n- Another new feature",
            "\n",
            "## 1.0.0 (2023-01-01)",
            "",
            "### Fixed",
            "- Bug fix",
            "",
            "### Added",
            "- New feature",
        ]

        assert result == expected
