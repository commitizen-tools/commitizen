from __future__ import annotations

import os.path
from difflib import SequenceMatcher
from operator import itemgetter
from pathlib import Path
from typing import Callable, cast

from commitizen import changelog, defaults, factory, git, out
from commitizen.changelog_formats import get_changelog_format
from commitizen.config import BaseConfig
from commitizen.cz.base import ChangelogReleaseHook, MessageBuilderHook
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


class Changelog:
    """Generate a changelog based on the commit history."""

    def __init__(self, config: BaseConfig, args):
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.encoding = self.config.settings["encoding"]
        self.cz = factory.commiter_factory(self.config)

        self.start_rev = args.get("start_rev") or self.config.settings.get(
            "changelog_start_rev"
        )
        self.file_name = args.get("file_name") or cast(
            str, self.config.settings.get("changelog_file")
        )
        if not isinstance(self.file_name, str):
            raise NotAllowed(
                "Changelog file name is broken.\n"
                "Check the flag `--file-name` in the terminal "
                f"or the setting `changelog_file` in {self.config.path}"
            )
        self.changelog_format = get_changelog_format(self.config, self.file_name)

        self.incremental = args["incremental"] or self.config.settings.get(
            "changelog_incremental"
        )
        self.dry_run = args["dry_run"]

        self.scheme = get_version_scheme(
            self.config.settings, args.get("version_scheme")
        )

        current_version = (
            args.get("current_version", config.settings.get("version")) or ""
        )
        self.current_version = self.scheme(current_version) if current_version else None

        self.unreleased_version = args["unreleased_version"]
        self.change_type_map = (
            self.config.settings.get("change_type_map") or self.cz.change_type_map
        )
        self.change_type_order = (
            self.config.settings.get("change_type_order")
            or self.cz.change_type_order
            or defaults.change_type_order
        )
        self.rev_range = args.get("rev_range")
        self.tag_format: str = (
            args.get("tag_format") or self.config.settings["tag_format"]
        )
        self.tag_rules = TagRules(
            scheme=self.scheme,
            tag_format=self.tag_format,
            legacy_tag_formats=self.config.settings["legacy_tag_formats"],
            ignored_tag_formats=self.config.settings["ignored_tag_formats"],
            merge_prereleases=args.get("merge_prerelease")
            or self.config.settings["changelog_merge_prerelease"],
        )

        self.template = (
            args.get("template")
            or self.config.settings.get("template")
            or self.changelog_format.template
        )
        self.extras = args.get("extras") or {}
        self.export_template_to = args.get("export_template")

    def _find_incremental_rev(self, latest_version: str, tags: list[GitTag]) -> str:
        """Try to find the 'start_rev'.

        We use a similarity approach. We know how to parse the version from the markdown
        changelog, but not the whole tag, we don't even know how's the tag made.

        This 'smart' function tries to find a similarity between the found version number
        and the available tag.

        The SIMILARITY_THRESHOLD is an empirical value, it may have to be adjusted based
        on our experience.
        """
        SIMILARITY_THRESHOLD = 0.89
        tag_ratio = map(
            lambda tag: (
                SequenceMatcher(
                    None, latest_version, strip_local_version(tag.name)
                ).ratio(),
                tag,
            ),
            tags,
        )
        try:
            score, tag = max(tag_ratio, key=itemgetter(0))
        except ValueError:
            raise NoRevisionError()
        if score < SIMILARITY_THRESHOLD:
            raise NoRevisionError()
        start_rev = tag.name
        return start_rev

    def write_changelog(
        self, changelog_out: str, lines: list[str], changelog_meta: changelog.Metadata
    ):
        changelog_hook: Callable | None = self.cz.changelog_hook
        with smart_open(self.file_name, "w", encoding=self.encoding) as changelog_file:
            partial_changelog: str | None = None
            if self.incremental:
                new_lines = changelog.incremental_build(
                    changelog_out, lines, changelog_meta
                )
                changelog_out = "".join(new_lines)
                partial_changelog = changelog_out

            if changelog_hook:
                changelog_out = changelog_hook(changelog_out, partial_changelog)

            changelog_file.write(changelog_out)

    def export_template(self):
        tpl = changelog.get_changelog_template(self.cz.template_loader, self.template)
        src = Path(tpl.filename)
        Path(self.export_template_to).write_text(src.read_text())

    def __call__(self):
        commit_parser = self.cz.commit_parser
        changelog_pattern = self.cz.changelog_pattern
        start_rev = self.start_rev
        unreleased_version = self.unreleased_version
        changelog_meta = changelog.Metadata()
        change_type_map: dict | None = self.change_type_map
        changelog_message_builder_hook: MessageBuilderHook | None = (
            self.cz.changelog_message_builder_hook
        )
        changelog_release_hook: ChangelogReleaseHook | None = (
            self.cz.changelog_release_hook
        )

        if self.export_template_to:
            return self.export_template()

        if not changelog_pattern or not commit_parser:
            raise NoPatternMapError(
                f"'{self.config.settings['name']}' rule does not support changelog"
            )

        if self.incremental and self.rev_range:
            raise NotAllowed("--incremental cannot be combined with a rev_range")

        # Don't continue if no `file_name` specified.
        assert self.file_name

        tags = self.tag_rules.get_version_tags(git.get_tags(), warn=True)
        end_rev = ""
        if self.incremental:
            changelog_meta = self.changelog_format.get_metadata(self.file_name)
            if changelog_meta.latest_version:
                start_rev = self._find_incremental_rev(
                    strip_local_version(changelog_meta.latest_version_tag), tags
                )
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
            unreleased_version,
            change_type_map=change_type_map,
            changelog_message_builder_hook=changelog_message_builder_hook,
            changelog_release_hook=changelog_release_hook,
            rules=self.tag_rules,
        )
        if self.change_type_order:
            tree = changelog.order_changelog_tree(tree, self.change_type_order)

        extras = self.cz.template_extras.copy()
        extras.update(self.config.settings["extras"])
        extras.update(self.extras)
        changelog_out = changelog.render_changelog(
            tree, loader=self.cz.template_loader, template=self.template, **extras
        )
        changelog_out = changelog_out.lstrip("\n")

        # Dry_run is executed here to avoid checking and reading the files
        if self.dry_run:
            changelog_hook: Callable | None = self.cz.changelog_hook
            if changelog_hook:
                changelog_out = changelog_hook(changelog_out, "")
            out.write(changelog_out)
            raise DryRunExit()

        lines = []
        if self.incremental and os.path.isfile(self.file_name):
            with open(self.file_name, encoding=self.encoding) as changelog_file:
                lines = changelog_file.readlines()

        self.write_changelog(changelog_out, lines, changelog_meta)
