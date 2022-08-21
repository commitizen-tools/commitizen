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

import os
import re
from collections import OrderedDict, defaultdict
from datetime import date
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from jinja2 import Environment, PackageLoader

from commitizen import defaults
from commitizen.bump import normalize_tag
from commitizen.exceptions import InvalidConfigurationError, NoCommitsFoundError
from commitizen.git import GitCommit, GitTag


def get_commit_tag(commit: GitCommit, tags: List[GitTag]) -> Optional[GitTag]:
    return next((tag for tag in tags if tag.rev == commit.rev), None)


def generate_tree_from_commits(
    commits: List[GitCommit],
    tags: List[GitTag],
    commit_parser: str,
    changelog_pattern: str,
    unreleased_version: Optional[str] = None,
    change_type_map: Optional[Dict[str, str]] = None,
    changelog_message_builder_hook: Optional[Callable] = None,
) -> Iterable[Dict]:
    pat = re.compile(changelog_pattern)
    map_pat = re.compile(commit_parser, re.MULTILINE)
    body_map_pat = re.compile(commit_parser, re.MULTILINE | re.DOTALL)

    # Check if the latest commit is not tagged
    latest_commit = commits[0]
    current_tag: Optional[GitTag] = get_commit_tag(latest_commit, tags)

    current_tag_name: str = unreleased_version or "Unreleased"
    current_tag_date: str = ""
    if unreleased_version is not None:
        current_tag_date = date.today().isoformat()
    if current_tag is not None and current_tag.name:
        current_tag_name = current_tag.name
        current_tag_date = current_tag.date

    changes: Dict = defaultdict(list)
    used_tags: List = [current_tag]
    for commit in commits:
        commit_tag = get_commit_tag(commit, tags)

        if commit_tag is not None and commit_tag not in used_tags:
            used_tags.append(commit_tag)
            yield {
                "version": current_tag_name,
                "date": current_tag_date,
                "changes": changes,
            }
            # TODO: Check if tag matches the version pattern, otherwise skip it.
            # This in order to prevent tags that are not versions.
            current_tag_name = commit_tag.name
            current_tag_date = commit_tag.date
            changes = defaultdict(list)

        matches = pat.match(commit.message)
        if not matches:
            continue

        # Process subject from commit message
        message = map_pat.match(commit.message)
        if message:
            parsed_message: Dict = message.groupdict()
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
            parsed_message_body: Dict = message_body.groupdict()

            change_type = parsed_message_body.pop("change_type", None)
            if change_type_map:
                change_type = change_type_map.get(change_type, change_type)
            changes[change_type].append(parsed_message_body)

    yield {"version": current_tag_name, "date": current_tag_date, "changes": changes}


def order_changelog_tree(tree: Iterable, change_type_order: List[str]) -> Iterable:
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


def parse_version_from_markdown(value: str) -> Optional[str]:
    if not value.startswith("#"):
        return None
    m = re.search(defaults.version_parser, value)
    if not m:
        return None
    return m.groupdict().get("version")


def parse_title_type_of_line(value: str) -> Optional[str]:
    md_title_parser = r"^(?P<title>#+)"
    m = re.search(md_title_parser, value)
    if not m:
        return None
    return m.groupdict().get("title")


def get_metadata(filepath: str) -> Dict:
    unreleased_start: Optional[int] = None
    unreleased_end: Optional[int] = None
    unreleased_title: Optional[str] = None
    latest_version: Optional[str] = None
    latest_version_position: Optional[int] = None
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

            unreleased: Optional[str] = None
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
            version = parse_version_from_markdown(line)
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


def incremental_build(new_content: str, lines: List[str], metadata: Dict) -> List[str]:
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
    output_lines: List[str] = []
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
    tags: List[GitTag], newest: str, oldest: Optional[str] = None
) -> List[GitTag]:
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
    tags: List[GitTag], version: str, tag_format: str
) -> Tuple[Optional[str], Optional[str]]:
    """Find the tags for the given version.

    `version` may come in different formats:
    - `0.1.0..0.4.0`: as a range
    - `0.3.0`: as a single version
    """
    oldest: Optional[str] = None
    newest: Optional[str] = None
    try:
        oldest, newest = version.split("..")
    except ValueError:
        newest = version

    newest_tag = normalize_tag(newest, tag_format=tag_format)

    oldest_tag = None
    if oldest:
        oldest_tag = normalize_tag(oldest, tag_format=tag_format)

    tags_range = get_smart_tag_range(tags, newest=newest_tag, oldest=oldest_tag)
    if not tags_range:
        raise NoCommitsFoundError("Could not find a valid revision range.")

    oldest_rev: Optional[str] = tags_range[-1].name
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
