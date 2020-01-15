import re
from collections import OrderedDict

from commitizen import factory, out, git
from commitizen.config import BaseConfig


class Changelog:
    """Generate a changelog based on the commit history."""

    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

        # TODO: make these argument
        self.skip_merge = True

    def __call__(self):
        changelog_map = self.cz.changelog_map
        changelog_pattern = self.cz.changelog_pattern
        if not changelog_map:
            out.error(
                f"'{self.config.settings['name']}' rule does not support changelog"
            )

        pat = re.compile(changelog_pattern)

        changelog_tree = OrderedDict({value: [] for value in changelog_map.values()})
        commits = git.get_commits()
        for commit in commits:
            if self.skip_merge and commit.startswith("Merge"):
                continue

            for message in commit.split("\n"):
                result = pat.search(message)
                if not result:
                    continue
                found_keyword = result.group(0)
                processed_commit = self.cz.process_commit(commit)
                changelog_tree[changelog_map[found_keyword]].append(processed_commit)
                break

        # TODO: handle rev
        # an entry of changelog contains 'rev -> change_type -> message'
        # the code above handles `change_type -> message` part
