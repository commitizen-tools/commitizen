"""
# DESIGN

## Parse CHANGELOG.md

1. Get LATEST VERSION from CONFIG
1. Parse the file version to version
2. Build a dict (tree) of that particular version
3. Transform tree into markdown again

## Parse git log

1. get commits between versions
2. filter commits with the current cz rules
3. parse commit information
4. generate tree

Options:
- Generate full or partial changelog
"""
from typing import Generator, List, Dict, Iterable
import re

MD_VERSION_RE = r"^##\s(?P<version>[a-zA-Z0-9.+]+)\s?\(?(?P<date>[0-9-]+)?\)?"
MD_CATEGORY_RE = r"^###\s(?P<category>[a-zA-Z0-9.+\s]+)"
MD_MESSAGE_RE = r"^-\s(\*{2}(?P<scope>[a-zA-Z0-9]+)\*{2}:\s)?(?P<message>.+)"
md_version_c = re.compile(MD_VERSION_RE)
md_category_c = re.compile(MD_CATEGORY_RE)
md_message_c = re.compile(MD_MESSAGE_RE)


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


def find_version_blocks(filepath: str) -> Generator:
    """
    version block: contains all the information about a version.

    E.g:
    ```
    ## 1.2.1 (2019-07-20)

    ## Bug fixes

    - username validation not working

    ## Features

    - new login system

    ```
    """
    with open(filepath, "r") as f:
        block: list = []
        for line in f:
            line = line.strip("\n")
            if not line:
                continue

            if line.startswith("## "):
                if len(block) > 0:
                    yield block
                block = [line]
            else:
                block.append(line)
        yield block


def parse_md_version(md_version: str) -> Dict:
    m = md_version_c.match(md_version)
    if not m:
        return {}
    return m.groupdict()


def parse_md_category(md_category: str) -> Dict:
    m = md_category_c.match(md_category)
    if not m:
        return {}
    return m.groupdict()


def parse_md_message(md_message: str) -> Dict:
    m = md_message_c.match(md_message)
    if not m:
        return {}
    return m.groupdict()


def transform_category(category: str) -> str:
    _category_lower = category.lower()
    for match_value, output in CATEGORIES:
        if re.search(match_value, _category_lower):
            return output
    else:
        raise ValueError(f"Could not match a category with {category}")


def generate_block_tree(block: List[str]) -> Dict:
    tree: Dict = {"commits": []}
    category = None
    for line in block:
        if line.startswith("## "):
            category = None
            tree = {**tree, **parse_md_version(line)}
        elif line.startswith("### "):
            result = parse_md_category(line)
            if not result:
                continue
            category = transform_category(result.get("category", ""))

        elif line.startswith("- "):
            commit = parse_md_message(line)
            commit["category"] = category
            tree["commits"].append(commit)
        else:
            print("it's something else: ", line)
    return tree


def generate_full_tree(blocks: Iterable) -> Iterable[Dict]:
    for block in blocks:
        yield generate_block_tree(block)
