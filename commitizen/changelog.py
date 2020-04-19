"""
# DESIGN

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
- Generate full or partial changelog
- Include in tree from file all the extra comments added manually
"""
import re
from collections import defaultdict
from typing import Dict, Iterable, List, Optional

import pkg_resources
from jinja2 import Template

from commitizen import defaults
from commitizen.git import GitCommit, GitProtocol, GitTag

CATEGORIES = [
    ("fix", "fix"),
    ("breaking", "BREAKING CHANGES"),
    ("feat", "feat"),
    ("refactor", "refactor"),
    ("perf", "perf"),
    ("test", "test"),
    ("build", "build"),
    ("ci", "ci"),
    ("chore", "chore"),
]


def transform_change_type(change_type: str) -> str:
    # TODO: Use again to parse, for this we have to wait until the maps get
    # defined again.
    _change_type_lower = change_type.lower()
    for match_value, output in CATEGORIES:
        if re.search(match_value, _change_type_lower):
            return output
    else:
        raise ValueError(f"Could not match a change_type with {change_type}")


def get_commit_tag(commit: GitProtocol, tags: List[GitProtocol]) -> Optional[GitTag]:
    """"""
    try:
        tag_index = tags.index(commit)
    except ValueError:
        return None
    else:
        tag = tags[tag_index]
        return tag


def generate_tree_from_commits(
    commits: List[GitCommit],
    tags: List[GitTag],
    commit_parser: str,
    changelog_pattern: str = defaults.bump_pattern,
) -> Iterable[Dict]:
    pat = re.compile(changelog_pattern)
    map_pat = re.compile(commit_parser)
    # Check if the latest commit is not tagged
    latest_commit = commits[0]
    current_tag: Optional[GitTag] = get_commit_tag(latest_commit, tags)

    current_tag_name: str = "Unreleased"
    current_tag_date: str = ""
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
            # TODO: Check if tag matches the version pattern, otherwie skip it.
            # This in order to prevent tags that are not versions.
            current_tag_name = commit_tag.name
            current_tag_date = commit_tag.date
            changes = defaultdict(list)

        matches = pat.match(commit.message)
        if not matches:
            continue

        message = map_pat.match(commit.message)
        message_body = map_pat.match(commit.body)
        if message:
            parsed_message: Dict = message.groupdict()
            # change_type becomes optional by providing None
            change_type = parsed_message.pop("change_type", None)
            changes[change_type].append(parsed_message)
        if message_body:
            parsed_message_body: Dict = message_body.groupdict()
            change_type = parsed_message_body.pop("change_type", None)
            changes[change_type].append(parsed_message_body)

    yield {
        "version": current_tag_name,
        "date": current_tag_date,
        "changes": changes,
    }


def render_changelog(tree: Iterable) -> str:
    template_file = pkg_resources.resource_string(
        __name__, "templates/keep_a_changelog_template.j2"
    ).decode("utf-8")
    jinja_template = Template(template_file, trim_blocks=True)
    changelog: str = jinja_template.render(tree=tree)
    return changelog
