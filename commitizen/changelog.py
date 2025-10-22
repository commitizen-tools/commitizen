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
from collections.abc import Generator, Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from datetime import date
from itertools import chain
from typing import TYPE_CHECKING, Any

from deprecated import deprecated
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

    def __post_init__(self) -> None:
        if self.latest_version and not self.latest_version_tag:
            # Test syntactic sugar
            # latest version tag is optional if same as latest version
            self.latest_version_tag = self.latest_version


def get_commit_tag(commit: GitCommit, tags: list[GitTag]) -> GitTag | None:
    return next((tag for tag in tags if tag.rev == commit.rev), None)


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
) -> Generator[dict[str, Any], None, None]:
    pat = re.compile(changelog_pattern)
    map_pat = re.compile(commit_parser, re.MULTILINE)
    body_map_pat = re.compile(commit_parser, re.MULTILINE | re.DOTALL)
    rules = rules or TagRules()

    # Check if the latest commit is not tagged

    current_tag = get_commit_tag(commits[0], tags) if commits else None
    current_tag_name = unreleased_version or "Unreleased"
    current_tag_date = (
        date.today().isoformat() if unreleased_version is not None else ""
    )

    used_tags: set[GitTag] = set()
    if current_tag:
        used_tags.add(current_tag)
        if current_tag.name:
            current_tag_name = current_tag.name
            current_tag_date = current_tag.date

    commit_tag: GitTag | None = None
    changes: dict = defaultdict(list)
    for commit in commits:
        if (
            (commit_tag := get_commit_tag(commit, tags))
            and commit_tag not in used_tags
            and rules.include_in_changelog(commit_tag)
        ):
            used_tags.add(commit_tag)
            release = {
                "version": current_tag_name,
                "date": current_tag_date,
                "changes": changes,
            }
            if changelog_release_hook:
                release = changelog_release_hook(release, commit_tag)
            yield release
            current_tag_name = commit_tag.name
            current_tag_date = commit_tag.date
            changes = defaultdict(list)

        if not pat.match(commit.message):
            continue

        # Process subject and body from commit message
        for message in chain(
            [map_pat.match(commit.message)],
            (body_map_pat.match(block) for block in commit.body.split("\n\n")),
        ):
            if message:
                process_commit_message(
                    changelog_message_builder_hook,
                    message,
                    commit,
                    changes,
                    change_type_map,
                )

    release = {
        "version": current_tag_name,
        "date": current_tag_date,
        "changes": changes,
    }
    if changelog_release_hook:
        release = changelog_release_hook(release, commit_tag)
    yield release


def process_commit_message(
    hook: MessageBuilderHook | None,
    parsed: re.Match[str],
    commit: GitCommit,
    ref_changes: MutableMapping[str | None, list],
    change_type_map: Mapping[str, str] | None = None,
) -> None:
    message: dict[str, Any] = {
        "sha1": commit.rev,
        "parents": commit.parents,
        "author": commit.author,
        "author_email": commit.author_email,
        **parsed.groupdict(),
    }

    processed_msg = hook(message, commit) if hook else message
    if not processed_msg:
        return

    messages = [processed_msg] if isinstance(processed_msg, dict) else processed_msg
    for msg in messages:
        change_type = msg.pop("change_type", None)
        if change_type_map:
            change_type = change_type_map.get(change_type, change_type)
        ref_changes[change_type].append(msg)


def generate_ordered_changelog_tree(
    tree: Iterable[Mapping[str, Any]], change_type_order: list[str]
) -> Generator[dict[str, Any], None, None]:
    if len(set(change_type_order)) != len(change_type_order):
        raise InvalidConfigurationError(
            f"Change types contain duplicated types ({change_type_order})"
        )

    for entry in tree:
        yield {
            **entry,
            "changes": _calculate_sorted_changes(change_type_order, entry["changes"]),
        }


def _calculate_sorted_changes(
    change_type_order: list[str], changes: Mapping[str, Any]
) -> OrderedDict[str, Any]:
    remaining_change_types = set(changes.keys()) - set(change_type_order)
    sorted_change_types = change_type_order + sorted(remaining_change_types)
    return OrderedDict((ct, changes[ct]) for ct in sorted_change_types if ct in changes)


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
    **kwargs: Any,
) -> str:
    jinja_template = get_changelog_template(loader, template)
    changelog: str = jinja_template.render(tree=tree, **kwargs)
    return changelog


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
        elif index == unreleased_end:
            skip = False
            if (
                latest_version_position is None
                or latest_version_position > unreleased_end
            ):
                continue

        if skip:
            continue

        if index == latest_version_position:
            output_lines.extend([new_content, "\n"])
        output_lines.append(line)

    if latest_version_position is not None:
        return output_lines

    if output_lines and output_lines[-1].strip():
        # Ensure at least one blank line between existing and new content.
        output_lines.append("\n")
    output_lines.append(new_content)
    return output_lines


def get_next_tag_name_after_version(tags: Iterable[GitTag], version: str) -> str | None:
    it = iter(tag.name for tag in tags)
    for name in it:
        if name == version:
            return next(it, None)

    raise NoCommitsFoundError(f"Could not find a valid revision range. {version=}")


@deprecated(
    reason="This function is unused and will be removed in v5",
    version="5.0.0",
    category=DeprecationWarning,
)
def get_smart_tag_range(
    tags: Sequence[GitTag], newest: str, oldest: str | None = None
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
    tags: Iterable[GitTag],
    version: str,
    rules: TagRules,
) -> tuple[str | None, str]:
    """Find the tags for the given version.

    `version` may come in different formats:
    - `0.1.0..0.4.0`: as a range
    - `0.3.0`: as a single version
    """
    oldest_version, sep, newest_version = version.partition("..")
    if not sep:
        newest_version = version
        oldest_version = ""

    def get_tag_name(v: str) -> str:
        if tag := rules.find_tag_for(tags, v):
            return tag.name
        raise NoCommitsFoundError("Could not find a valid revision range.")

    newest_tag_name = get_tag_name(newest_version)
    oldest_tag_name = get_tag_name(oldest_version) if oldest_version else None

    oldest_rev = get_next_tag_name_after_version(
        tags, oldest_tag_name or newest_tag_name
    )

    # Return None for oldest_rev if:
    # 1. The oldest tag is the last tag in the list and matches the requested oldest tag
    # 2. The oldest and the newest tag are the same
    if oldest_rev == newest_tag_name:
        return None, newest_tag_name
    return oldest_rev, newest_tag_name
