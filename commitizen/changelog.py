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

import os
import re
from collections import OrderedDict, defaultdict
from datetime import date
from typing import TYPE_CHECKING, Callable, Iterable, Type, cast

from jinja2 import Environment, PackageLoader

from commitizen import out
from commitizen.bump import normalize_tag
from commitizen.exceptions import InvalidConfigurationError, NoCommitsFoundError
from commitizen.git import GitCommit, GitTag
from commitizen.version_schemes import (
    DEFAULT_SCHEME,
    BaseVersion,
    InvalidVersion,
    Pep440,
)

if TYPE_CHECKING:
    from commitizen.version_schemes import VersionScheme


def get_commit_tag(commit: GitCommit, tags: list[GitTag]) -> GitTag | None:
    return next((tag for tag in tags if tag.rev == commit.rev), None)


def tag_included_in_changelog(
    tag: GitTag,
    used_tags: list,
    merge_prerelease: bool,
    scheme: VersionScheme = DEFAULT_SCHEME,
) -> bool:
    if tag in used_tags:
        return False

    try:
        version = scheme(tag.name)
    except InvalidVersion:
        return False

    if merge_prerelease and version.is_prerelease:
        return False

    return True


def get_version_tags(scheme: Type[BaseVersion], tags: list[GitTag]) -> list[GitTag]:
    valid_tags: list[GitTag] = []
    for tag in tags:
        try:
            scheme(tag.name)
        except InvalidVersion:
            out.warn(f"InvalidVersion {tag}")
        else:
            valid_tags.append(tag)

    return valid_tags


def generate_tree_from_commits(
    commits: list[GitCommit],
    tags: list[GitTag],
    commit_parser: str,
    changelog_pattern: str,
    unreleased_version: str | None = None,
    change_type_map: dict[str, str] | None = None,
    changelog_message_builder_hook: Callable | None = None,
    merge_prerelease: bool = False,
    scheme: VersionScheme = DEFAULT_SCHEME,
) -> Iterable[dict]:
    pat = re.compile(changelog_pattern)
    map_pat = re.compile(commit_parser, re.MULTILINE)
    body_map_pat = re.compile(commit_parser, re.MULTILINE | re.DOTALL)
    current_tag: GitTag | None = None

    # Check if the latest commit is not tagged
    if commits:
        latest_commit = commits[0]
        current_tag = get_commit_tag(latest_commit, tags)

    current_tag_name: str = unreleased_version or "Unreleased"
    current_tag_date: str = ""
    if unreleased_version is not None:
        current_tag_date = date.today().isoformat()
    if current_tag is not None and current_tag.name:
        current_tag_name = current_tag.name
        current_tag_date = current_tag.date

    changes: dict = defaultdict(list)
    used_tags: list = [current_tag]
    for commit in commits:
        commit_tag = get_commit_tag(commit, tags)

        if commit_tag is not None and tag_included_in_changelog(
            commit_tag, used_tags, merge_prerelease, scheme=scheme
        ):
            used_tags.append(commit_tag)
            yield {
                "version": current_tag_name,
                "date": current_tag_date,
                "changes": changes,
            }
            current_tag_name = commit_tag.name
            current_tag_date = commit_tag.date
            changes = defaultdict(list)

        matches = pat.match(commit.message)
        if not matches:
            continue

        # Process subject from commit message
        message = map_pat.match(commit.message)
        if message:
            parsed_message: dict = message.groupdict()
            # change_type becomes optional by providing None
            change_type = parsed_message.pop("change_type", None)

            if change_type_map:
                change_type = change_type_map.get(change_type, change_type)
            if changelog_message_builder_hook:
                parsed_message = changelog_message_builder_hook(parsed_message, commit)
            changes[change_type].append(parsed_message)

        # Process body from commit message
        body_parts = commit.body.split("\n\n")
        for body_part in body_parts:
            message_body = body_map_pat.match(body_part)
            if not message_body:
                continue
            parsed_message_body: dict = message_body.groupdict()

            change_type = parsed_message_body.pop("change_type", None)
            if change_type_map:
                change_type = change_type_map.get(change_type, change_type)
            changes[change_type].append(parsed_message_body)

    yield {"version": current_tag_name, "date": current_tag_date, "changes": changes}


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


def render_changelog(tree: Iterable) -> str:
    loader = PackageLoader("commitizen", "templates")
    env = Environment(loader=loader, trim_blocks=True)
    jinja_template = env.get_template("keep_a_changelog_template.j2")
    changelog: str = jinja_template.render(tree=tree)
    return changelog


def parse_version_from_markdown(
    value: str, scheme: VersionScheme = Pep440
) -> str | None:
    if not value.startswith("#"):
        return None
    m = scheme.parser.search(value)
    if not m:
        return None
    return cast(str, m.group("version"))


def parse_title_type_of_line(value: str) -> str | None:
    md_title_parser = r"^(?P<title>#+)"
    m = re.search(md_title_parser, value)
    if not m:
        return None
    return m.groupdict().get("title")


def get_metadata(filepath: str, scheme: VersionScheme = Pep440) -> dict:
    unreleased_start: int | None = None
    unreleased_end: int | None = None
    unreleased_title: str | None = None
    latest_version: str | None = None
    latest_version_position: int | None = None
    if not os.path.isfile(filepath):
        return {
            "unreleased_start": None,
            "unreleased_end": None,
            "latest_version": None,
            "latest_version_position": None,
        }

    with open(filepath, "r") as changelog_file:
        for index, line in enumerate(changelog_file):
            line = line.strip().lower()

            unreleased: str | None = None
            if "unreleased" in line:
                unreleased = parse_title_type_of_line(line)
            # Try to find beginning and end lines of the unreleased block
            if unreleased:
                unreleased_start = index
                unreleased_title = unreleased
                continue
            elif (
                isinstance(unreleased_title, str)
                and parse_title_type_of_line(line) == unreleased_title
            ):
                unreleased_end = index

            # Try to find the latest release done
            version = parse_version_from_markdown(line, scheme)
            if version:
                latest_version = version
                latest_version_position = index
                break  # there's no need for more info
        if unreleased_start is not None and unreleased_end is None:
            unreleased_end = index
    return {
        "unreleased_start": unreleased_start,
        "unreleased_end": unreleased_end,
        "latest_version": latest_version,
        "latest_version_position": latest_version_position,
    }


def incremental_build(new_content: str, lines: list[str], metadata: dict) -> list[str]:
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
    unreleased_start = metadata.get("unreleased_start")
    unreleased_end = metadata.get("unreleased_end")
    latest_version_position = metadata.get("latest_version_position")
    skip = False
    output_lines: list[str] = []
    for index, line in enumerate(lines):
        if index == unreleased_start:
            skip = True
        elif index == unreleased_end:
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
    if not isinstance(latest_version_position, int):
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
    tag_format: str,
    scheme: VersionScheme | None = None,
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

    newest_tag = normalize_tag(newest, tag_format=tag_format, scheme=scheme)

    oldest_tag = None
    if oldest:
        oldest_tag = normalize_tag(oldest, tag_format=tag_format, scheme=scheme)

    tags_range = get_smart_tag_range(tags, newest=newest_tag, oldest=oldest_tag)
    if not tags_range:
        raise NoCommitsFoundError("Could not find a valid revision range.")

    oldest_rev: str | None = tags_range[-1].name
    newest_rev = newest_tag

    # check if it's the first tag created
    # and it's also being requested as part of the range
    if oldest_rev == tags[-1].name and oldest_rev == oldest_tag:
        return None, newest_rev

    # when they are the same, and it's also the
    # first tag created
    if oldest_rev == newest_rev:
        return None, newest_rev

    return oldest_rev, newest_rev
