from __future__ import annotations

import os
import os.path
from collections.abc import Generator, Iterable
from difflib import SequenceMatcher
from operator import itemgetter
from pathlib import Path
from typing import Any, TypedDict, cast

from commitizen import changelog, defaults, factory, git, out
from commitizen.changelog_formats import get_changelog_format
from commitizen.config import BaseConfig
from commitizen.cz.utils import strip_local_version
from commitizen.exceptions import (
    DryRunExit,
    NoCommitsFoundError,
    NoPatternMapError,
    NoRevisionError,
    NotAGitProjectError,
    NotAllowed,
)
from commitizen.git import GitTag, smart_open
from commitizen.tags import TagRules
from commitizen.version_schemes import get_version_scheme


class ChangelogArgs(TypedDict, total=False):
    change_type_map: dict[str, str]
    change_type_order: list[str]
    current_version: str
    dry_run: bool
    file_name: str
    incremental: bool
    merge_prerelease: bool
    rev_range: str
    start_rev: str
    tag_format: str
    unreleased_version: str | None
    version_scheme: str
    template: str
    extras: dict[str, Any]
    export_template: str


class Changelog:
    """Generate a changelog based on the commit history."""

    def __init__(self, config: BaseConfig, arguments: ChangelogArgs) -> None:
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config = config

        changelog_file_name = arguments.get("file_name") or self.config.settings.get(
            "changelog_file"
        )
        if not isinstance(changelog_file_name, str):
            raise NotAllowed(
                "Changelog file name is broken.\n"
                "Check the flag `--file-name` in the terminal "
                f"or the setting `changelog_file` in {self.config.path}"
            )
        self.file_name = (
            os.path.join(str(self.config.path.parent), changelog_file_name)
            if self.config.path is not None
            else changelog_file_name
        )

        self.encoding = self.config.settings["encoding"]
        self.cz = factory.committer_factory(self.config)

        self.start_rev = arguments.get("start_rev") or self.config.settings.get(
            "changelog_start_rev"
        )

        self.changelog_format = get_changelog_format(self.config, self.file_name)

        self.incremental = bool(
            arguments.get("incremental")
            or self.config.settings.get("changelog_incremental")
        )
        self.dry_run = bool(arguments.get("dry_run"))

        self.scheme = get_version_scheme(
            self.config.settings, arguments.get("version_scheme")
        )

        current_version = (
            arguments.get("current_version")
            or self.config.settings.get("version")
            or ""
        )
        self.current_version = self.scheme(current_version) if current_version else None

        self.unreleased_version = arguments["unreleased_version"]
        self.change_type_map = (
            self.config.settings.get("change_type_map") or self.cz.change_type_map
        )
        self.change_type_order = cast(
            list[str],
            self.config.settings.get("change_type_order")
            or self.cz.change_type_order
            or defaults.CHANGE_TYPE_ORDER,
        )
        self.rev_range = arguments.get("rev_range")
        self.tag_format = (
            arguments.get("tag_format") or self.config.settings["tag_format"]
        )
        self.tag_rules = TagRules(
            scheme=self.scheme,
            tag_format=self.tag_format,
            legacy_tag_formats=self.config.settings["legacy_tag_formats"],
            ignored_tag_formats=self.config.settings["ignored_tag_formats"],
            merge_prereleases=arguments.get("merge_prerelease")
            or self.config.settings["changelog_merge_prerelease"],
        )

        self.template = (
            arguments.get("template")
            or self.config.settings.get("template")
            or self.changelog_format.template
        )
        self.extras = arguments.get("extras") or {}
        self.export_template_to = arguments.get("export_template")

    def _find_incremental_rev(self, latest_version: str, tags: Iterable[GitTag]) -> str:
        """Try to find the 'start_rev'.

        We use a similarity approach. We know how to parse the version from the markdown
        changelog, but not the whole tag, we don't even know how's the tag made.

        This 'smart' function tries to find a similarity between the found version number
        and the available tag.

        The SIMILARITY_THRESHOLD is an empirical value, it may have to be adjusted based
        on our experience.
        """
        SIMILARITY_THRESHOLD = 0.89
        scores_and_tag_names: Generator[tuple[float, str]] = (
            (
                score,
                tag.name,
            )
            for tag in tags
            if (
                score := SequenceMatcher(
                    None, latest_version, strip_local_version(tag.name)
                ).ratio()
            )
            >= SIMILARITY_THRESHOLD
        )
        try:
            _, start_rev = max(scores_and_tag_names, key=itemgetter(0))
        except ValueError:
            raise NoRevisionError()
        return start_rev

    def _write_changelog(
        self, changelog_out: str, lines: list[str], changelog_meta: changelog.Metadata
    ) -> None:
        with smart_open(self.file_name, "w", encoding=self.encoding) as changelog_file:
            partial_changelog: str | None = None
            if self.incremental:
                new_lines = changelog.incremental_build(
                    changelog_out, lines, changelog_meta
                )
                changelog_out = "".join(new_lines)
                partial_changelog = changelog_out

            if self.cz.changelog_hook:
                changelog_out = self.cz.changelog_hook(changelog_out, partial_changelog)

            changelog_file.write(changelog_out)

    def _export_template(self, dist: str) -> None:
        filename = changelog.get_changelog_template(
            self.cz.template_loader, self.template
        ).filename
        if filename is None:
            raise NotAllowed("Template filename is not set")

        text = Path(filename).read_text()
        Path(dist).write_text(text)

    def __call__(self) -> None:
        commit_parser = self.cz.commit_parser
        changelog_pattern = self.cz.changelog_pattern
        start_rev = self.start_rev

        if self.export_template_to:
            return self._export_template(self.export_template_to)

        if not changelog_pattern or not commit_parser:
            raise NoPatternMapError(
                f"'{self.config.settings['name']}' rule does not support changelog"
            )

        if self.incremental and self.rev_range:
            raise NotAllowed("--incremental cannot be combined with a rev_range")

        # Don't continue if no `file_name` specified.
        assert self.file_name

        tags = self.tag_rules.get_version_tags(git.get_tags(), warn=True)
        changelog_meta = changelog.Metadata()
        if self.incremental:
            changelog_meta = self.changelog_format.get_metadata(self.file_name)
            if changelog_meta.latest_version:
                start_rev = self._find_incremental_rev(
                    strip_local_version(changelog_meta.latest_version_tag or ""), tags
                )

        end_rev = ""
        if self.rev_range:
            start_rev, end_rev = changelog.get_oldest_and_newest_rev(
                tags,
                self.rev_range,
                self.tag_rules,
            )

        commits = git.get_commits(start=start_rev, end=end_rev, args="--topo-order")
        if not commits and (
            self.current_version is None or not self.current_version.is_prerelease
        ):
            raise NoCommitsFoundError("No commits found")

        tree = changelog.generate_tree_from_commits(
            commits,
            tags,
            commit_parser,
            changelog_pattern,
            self.unreleased_version,
            change_type_map=self.change_type_map,
            changelog_message_builder_hook=self.cz.changelog_message_builder_hook,
            changelog_release_hook=self.cz.changelog_release_hook,
            rules=self.tag_rules,
        )
        if self.change_type_order:
            tree = changelog.generate_ordered_changelog_tree(
                tree, self.change_type_order
            )

        changelog_out = changelog.render_changelog(
            tree,
            self.cz.template_loader,
            self.template,
            **{
                **self.cz.template_extras,
                **self.config.settings["extras"],
                **self.extras,
            },
        ).lstrip("\n")

        # Dry_run is executed here to avoid checking and reading the files
        if self.dry_run:
            if self.cz.changelog_hook:
                changelog_out = self.cz.changelog_hook(changelog_out, "")
            out.write(changelog_out)
            raise DryRunExit()

        lines = []
        if self.incremental and os.path.isfile(self.file_name):
            with open(self.file_name, encoding=self.encoding) as changelog_file:
                lines = changelog_file.readlines()

        self._write_changelog(changelog_out, lines, changelog_meta)
