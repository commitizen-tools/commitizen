import os.path
from difflib import SequenceMatcher
from operator import itemgetter
from typing import Callable, Dict, List, Optional

from commitizen import bump, changelog, defaults, factory, git, out
from commitizen.config import BaseConfig
from commitizen.exceptions import (
    DryRunExit,
    NoCommitsFoundError,
    NoPatternMapError,
    NoRevisionError,
    NotAGitProjectError,
    NotAllowed,
)
from commitizen.git import GitTag, smart_open


class Changelog:
    """Generate a changelog based on the commit history."""

    def __init__(self, config: BaseConfig, args):
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

        self.start_rev = args.get("start_rev") or self.config.settings.get(
            "changelog_start_rev"
        )
        self.file_name = args.get("file_name") or self.config.settings.get(
            "changelog_file"
        )
        self.incremental = args["incremental"] or self.config.settings.get(
            "changelog_incremental"
        )
        self.dry_run = args["dry_run"]
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
        self.tag_format = args.get("tag_format") or self.config.settings.get(
            "tag_format"
        )

    def _find_incremental_rev(self, latest_version: str, tags: List[GitTag]) -> str:
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
            lambda tag: (SequenceMatcher(None, latest_version, tag.name).ratio(), tag),
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
        self, changelog_out: str, lines: List[str], changelog_meta: Dict
    ):
        if not isinstance(self.file_name, str):
            raise NotAllowed(
                "Changelog file name is broken.\n"
                "Check the flag `--file-name` in the terminal "
                f"or the setting `changelog_file` in {self.config.path}"
            )

        changelog_hook: Optional[Callable] = self.cz.changelog_hook
        with smart_open(self.file_name, "w") as changelog_file:
            partial_changelog: Optional[str] = None
            if self.incremental:
                new_lines = changelog.incremental_build(
                    changelog_out, lines, changelog_meta
                )
                changelog_out = "".join(new_lines)
                partial_changelog = changelog_out

            if changelog_hook:
                changelog_out = changelog_hook(changelog_out, partial_changelog)
            changelog_file.write(changelog_out)

    def __call__(self):
        commit_parser = self.cz.commit_parser
        changelog_pattern = self.cz.changelog_pattern
        start_rev = self.start_rev
        unreleased_version = self.unreleased_version
        changelog_meta: Dict = {}
        change_type_map: Optional[Dict] = self.change_type_map
        changelog_message_builder_hook: Optional[
            Callable
        ] = self.cz.changelog_message_builder_hook

        if not changelog_pattern or not commit_parser:
            raise NoPatternMapError(
                f"'{self.config.settings['name']}' rule does not support changelog"
            )

        if self.incremental and self.rev_range:
            raise NotAllowed("--incremental cannot be combined with a rev_range")

        # Don't continue if no `file_name` specified.
        assert self.file_name

        tags = git.get_tags()
        if not tags:
            tags = []

        end_rev = ""

        if self.incremental:
            changelog_meta = changelog.get_metadata(self.file_name)
            latest_version = changelog_meta.get("latest_version")
            if latest_version:
                latest_tag_version: str = bump.normalize_tag(
                    latest_version, tag_format=self.tag_format
                )
                start_rev = self._find_incremental_rev(latest_tag_version, tags)

        if self.rev_range:
            start_rev, end_rev = changelog.get_oldest_and_newest_rev(
                tags,
                version=self.rev_range,
                tag_format=self.tag_format,
            )

        commits = git.get_commits(
            start=start_rev, end=end_rev, args="--author-date-order"
        )
        if not commits:
            raise NoCommitsFoundError("No commits found")

        tree = changelog.generate_tree_from_commits(
            commits,
            tags,
            commit_parser,
            changelog_pattern,
            unreleased_version,
            change_type_map=change_type_map,
            changelog_message_builder_hook=changelog_message_builder_hook,
        )
        if self.change_type_order:
            tree = changelog.order_changelog_tree(tree, self.change_type_order)
        changelog_out = changelog.render_changelog(tree)
        changelog_out = changelog_out.lstrip("\n")

        if self.dry_run:
            out.write(changelog_out)
            raise DryRunExit()

        lines = []
        if self.incremental and os.path.isfile(self.file_name):
            with open(self.file_name, "r") as changelog_file:
                lines = changelog_file.readlines()

        self.write_changelog(changelog_out, lines, changelog_meta)
