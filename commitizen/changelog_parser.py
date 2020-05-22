"""CHNAGLOG PARSER DESIGN

## Parse CHANGELOG.md

1. Get LATEST VERSION from CONFIG
1. Parse the file version to version
2. Build a dict (tree) of that particular version
3. Transform tree into markdown again
"""
import re
from collections import defaultdict
from typing import Dict, Generator, Iterable, List

MD_VERSION_RE = r"^##\s(?P<version>[a-zA-Z0-9.+]+)\s?\(?(?P<date>[0-9-]+)?\)?"
MD_CHANGE_TYPE_RE = r"^###\s(?P<change_type>[a-zA-Z0-9.+\s]+)"
MD_MESSAGE_RE = (
    r"^-\s(\*{2}(?P<scope>[a-zA-Z0-9]+)\*{2}:\s)?(?P<message>.+)(?P<breaking>!)?"
)
md_version_c = re.compile(MD_VERSION_RE)
md_change_type_c = re.compile(MD_CHANGE_TYPE_RE)
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
    """Find version block (version block: contains all the information about a version.)

    E.g:
    ```
    ## 1.2.1 (2019-07-20)

    ### Fix

    - username validation not working

    ### Feat

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


def parse_md_change_type(md_change_type: str) -> Dict:
    m = md_change_type_c.match(md_change_type)
    if not m:
        return {}
    return m.groupdict()


def parse_md_message(md_message: str) -> Dict:
    m = md_message_c.match(md_message)
    if not m:
        return {}
    return m.groupdict()


def transform_change_type(change_type: str) -> str:
    # TODO: Use again to parse, for this we have to wait until the maps get
    # defined again.
    _change_type_lower = change_type.lower()
    for match_value, output in CATEGORIES:
        if re.search(match_value, _change_type_lower):
            return output
    else:
        raise ValueError(f"Could not match a change_type with {change_type}")


def generate_block_tree(block: List[str]) -> Dict:
    # tree: Dict = {"commits": []}
    changes: Dict = defaultdict(list)
    tree: Dict = {"changes": changes}

    change_type = None
    for line in block:
        if line.startswith("## "):
            # version identified
            change_type = None
            tree = {**tree, **parse_md_version(line)}
        elif line.startswith("### "):
            # change_type identified
            result = parse_md_change_type(line)
            if not result:
                continue
            change_type = result.get("change_type", "").lower()

        elif line.startswith("- "):
            # message identified
            commit = parse_md_message(line)
            changes[change_type].append(commit)
        else:
            print("it's something else: ", line)
    return tree


def generate_full_tree(blocks: Iterable) -> Iterable[Dict]:
    for block in blocks:
        yield generate_block_tree(block)
