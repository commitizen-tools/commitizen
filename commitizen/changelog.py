"""Design

## Metadata CHANGELOG.md

1. Identify irrelevant information (possible: changelog title, first paragraph)
2. Identify Unreleased area
3. Identify latest version (to be able to write on top of it)

## Parse git log

1. get commits between versions
2. filter commits with the current cz rules
3. parse commit information
4. yield tree nodes
5. format tree nodes
6. produce full tree
7. generate changelog

Extra:
- [x] Generate full or partial changelog
- [x] Include in tree from file all the extra comments added manually
- [x] Add unreleased value
- [x] hook after message is parsed (add extra information like hyperlinks)
- [x] hook after changelog is generated (api calls)
- [x] add support for change_type maps
"""

from __future__ import annotations

import re
from collections import OrderedDict, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from jinja2 import (
    BaseLoader,
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    Template,
)

from commitizen.cz.base import ChangelogReleaseHook
from commitizen.exceptions import InvalidConfigurationError, NoCommitsFoundError
from commitizen.git import GitCommit, GitTag
from commitizen.tags import TagRules

if TYPE_CHECKING:
    from commitizen.cz.base import MessageBuilderHook


@dataclass
class Metadata:
    """
    Metadata extracted from the changelog produced by a plugin
    """

    unreleased_start: int | None = None
    unreleased_end: int | None = None
    latest_version: str | None = None
    latest_version_position: int | None = None
    latest_version_tag: str | None = None

    def __post_init__(self):
        if self.latest_version and not self.latest_version_tag:
            # Test syntactic sugar
            # latest version tag is optional if same as latest version
            self.latest_version_tag = self.latest_version


def get_commit_tag(commit: GitCommit, tags: list[GitTag]) -> GitTag | None:
    return next((tag for tag in tags if tag.rev == commit.rev), None)


def _get_release_info(
    current_tag_name: str,
    current_tag_date: str,
    changes: dict[str | None, list],
    changelog_release_hook: ChangelogReleaseHook | None,
    commit_tag: GitTag | None,
) -> dict[str, Any]:
    release = {
        "version": current_tag_name,
        "date": current_tag_date,
        "changes": changes,
    }
    if changelog_release_hook:
        return changelog_release_hook(release, commit_tag)
    return release


def generate_tree_from_commits(
    commits: list[GitCommit],
    tags: list[GitTag],
    commit_parser: str,
    changelog_pattern: str,
    unreleased_version: str | None = None,
    change_type_map: dict[str, str] | None = None,
    changelog_message_builder_hook: MessageBuilderHook | None = None,
    changelog_release_hook: ChangelogReleaseHook | None = None,
    rules: TagRules | None = None,
) -> Iterable[dict]:
    pat = re.compile(changelog_pattern)
    map_pat = re.compile(commit_parser, re.MULTILINE)
    body_map_pat = re.compile(commit_parser, re.MULTILINE | re.DOTALL)
    rules = rules or TagRules()

    used_tags: set[GitTag] = set()
    current_tag_name = unreleased_version or "Unreleased"
    current_tag_date = (
        date.today().isoformat() if unreleased_version is not None else ""
    )

    # Check if the latest commit is not tagged
    current_tag = get_commit_tag(commits[0], tags) if commits else None
    if current_tag is not None:
        used_tags.add(current_tag)
        if current_tag.name:
            current_tag_name = current_tag.name
            current_tag_date = current_tag.date

    changes: defaultdict[str | None, list] = defaultdict(list)
    commit_tag: GitTag | None = None
    for commit in commits:
        commit_tag = get_commit_tag(commit, tags)

        if (
            commit_tag
            and commit_tag not in used_tags
            and rules.include_in_changelog(commit_tag)
        ):
            used_tags.add(commit_tag)

            yield _get_release_info(
                current_tag_name,
                current_tag_date,
                changes,
                changelog_release_hook,
                commit_tag,
            )

            current_tag_name = commit_tag.name
            current_tag_date = commit_tag.date
            changes = defaultdict(list)

        if not pat.match(commit.message):
            continue

        # Process subject from commit message
        if message := map_pat.match(commit.message):
            process_commit_message(
                changelog_message_builder_hook,
                message,
                commit,
                changes,
                change_type_map,
            )

        # Process body from commit message
        body_parts = commit.body.split("\n\n")
        for body_part in body_parts:
            if message := body_map_pat.match(body_part):
                process_commit_message(
                    changelog_message_builder_hook,
                    message,
                    commit,
                    changes,
                    change_type_map,
                )

    yield _get_release_info(
        current_tag_name,
        current_tag_date,
        changes,
        changelog_release_hook,
        commit_tag,
    )


def process_commit_message(
    hook: MessageBuilderHook | None,
    parsed: re.Match[str],
    commit: GitCommit,
    changes: dict[str | None, list],
    change_type_map: dict[str, str] | None = None,
):
    message: dict[str, str | list[str] | Any] = {
        "sha1": commit.rev,
        "parents": commit.parents,
        "author": commit.author,
        "author_email": commit.author_email,
        **parsed.groupdict(),
    }

    if not (processed := hook(message, commit) if hook else message):
        return

    processed_messages = [processed] if isinstance(processed, dict) else processed
    for msg in processed_messages:
        change_type = msg.pop("change_type", None)
        if change_type_map:
            change_type = change_type_map.get(change_type, change_type)
        changes[change_type].append(msg)


def order_changelog_tree(tree: Iterable, change_type_order: list[str]) -> Iterable:
    if len(set(change_type_order)) != len(change_type_order):
        raise InvalidConfigurationError(
            f"Change types contain duplicates types ({change_type_order})"
        )

    sorted_tree = []
    for entry in tree:
        ordered_change_types = change_type_order + sorted(
            set(entry["changes"].keys()) - set(change_type_order)
        )
        changes = [
            (ct, entry["changes"][ct])
            for ct in ordered_change_types
            if ct in entry["changes"]
        ]
        sorted_tree.append({**entry, **{"changes": OrderedDict(changes)}})
    return sorted_tree


def get_changelog_template(loader: BaseLoader, template: str) -> Template:
    loader = ChoiceLoader(
        [
            FileSystemLoader("."),
            loader,
        ]
    )
    env = Environment(loader=loader, trim_blocks=True)
    return env.get_template(template)


def render_changelog(
    tree: Iterable,
    loader: BaseLoader,
    template: str,
    **kwargs,
) -> str:
    jinja_template = get_changelog_template(loader, template)
    return jinja_template.render(tree=tree, **kwargs)


def incremental_build(
    new_content: str, lines: list[str], metadata: Metadata
) -> list[str]:
    """Takes the original lines and updates with new_content.

    The metadata governs how to remove the old unreleased section and where to place the
    new content.

    Args:
        lines: The lines from the changelog
        new_content: This should be placed somewhere in the lines
        metadata: Information about the changelog

    Returns:
        Updated lines
    """
    unreleased_start = metadata.unreleased_start
    unreleased_end = metadata.unreleased_end
    latest_version_position = metadata.latest_version_position
    skip = False
    output_lines: list[str] = []
    for index, line in enumerate(lines):
        if index == unreleased_start:
            skip = True
            continue

        if index == unreleased_end:
            skip = False
            if (
                latest_version_position is None
                or isinstance(latest_version_position, int)
                and isinstance(unreleased_end, int)
                and latest_version_position > unreleased_end
            ):
                continue

        if skip:
            continue

        if index == latest_version_position:
            output_lines.extend([new_content, "\n"])
        output_lines.append(line)

    if isinstance(latest_version_position, int):
        return output_lines

    if output_lines and output_lines[-1].strip():
        # Ensure at least one blank line between existing and new content.
        output_lines.append("\n")
    output_lines.append(new_content)
    return output_lines


def get_smart_tag_range(
    tags: list[GitTag], newest: str, oldest: str | None = None
) -> list[GitTag]:
    """Smart because it finds the N+1 tag.

    This is because we need to find until the next tag
    """
    accumulator = []
    keep = False
    if not oldest:
        oldest = newest
    for index, tag in enumerate(tags):
        if tag.name == newest:
            keep = True
        if keep:
            accumulator.append(tag)
        if tag.name == oldest:
            keep = False
            try:
                accumulator.append(tags[index + 1])
            except IndexError:
                pass
            break
    return accumulator


def get_oldest_and_newest_rev(
    tags: list[GitTag],
    version: str,
    rules: TagRules,
) -> tuple[str | None, str | None]:
    """Find the tags for the given version.

    `version` may come in different formats:
    - `0.1.0..0.4.0`: as a range
    - `0.3.0`: as a single version
    """
    oldest: str | None = None
    newest: str | None = None
    try:
        oldest, newest = version.split("..")
    except ValueError:
        newest = version
    if not (newest_tag := rules.find_tag_for(tags, newest)):
        raise NoCommitsFoundError("Could not find a valid revision range.")

    oldest_tag_name: str | None = None
    if oldest:
        if not (oldest_tag := rules.find_tag_for(tags, oldest)):
            raise NoCommitsFoundError("Could not find a valid revision range.")
        oldest_tag_name = oldest_tag.name

    tags_range = get_smart_tag_range(
        tags, newest=newest_tag.name, oldest=oldest_tag_name
    )
    if not tags_range:
        raise NoCommitsFoundError("Could not find a valid revision range.")

    newest_rev = newest_tag.name

    # Return None for oldest_rev if:
    # 1. The oldest tag is the last tag in the list and matches the requested oldest tag, or
    # 2. The oldest and newest tags are the same
    oldest_rev: str | None = (
        None
        if (
            tags_range[-1].name == tags[-1].name
            and tags_range[-1].name == oldest_tag_name
            or tags_range[-1].name == newest_rev
        )
        else tags_range[-1].name
    )

    return oldest_rev, newest_rev
