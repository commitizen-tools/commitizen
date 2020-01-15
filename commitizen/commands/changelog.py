import re
from collections import OrderedDict

from commitizen import factory, out, git
from commitizen.config import BaseConfig


class Changelog:
    """Generate a changelog based on the commit history."""

    def __init__(self, config: BaseConfig, *args):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

        # TODO: make these attribute arguments
        self.skip_merge = True
        self.file_name = "CHANGELOG.md"

    def __call__(self):
        changelog_map = self.cz.changelog_map
        changelog_pattern = self.cz.changelog_pattern
        if not changelog_map:
            out.error(
                f"'{self.config.settings['name']}' rule does not support changelog"
            )

        pat = re.compile(changelog_pattern)

        changelog_entry_key = "Unreleased"
        changelog_entry_values = OrderedDict(
            {value: [] for value in changelog_map.values()}
        )
        commits = git.get_commits()
        tag_map = {tag.rev: tag.name for tag in git.get_tags()}

        changelog_str = "# Changelog\n"
        for commit in commits:
            if self.skip_merge and commit.message.startswith("Merge"):
                continue

            if commit.rev in tag_map:
                changelog_str += f"\n## {changelog_entry_key}\n"
                for key, values in changelog_entry_values.items():
                    if not values:
                        continue
                    changelog_str += f"* {key}\n"
                    for value in values:
                        changelog_str += f"    * {value}\n"
                changelog_entry_key = tag_map[commit.rev]

            for message in commit.message.split("\n"):
                result = pat.search(message)
                if not result:
                    continue
                found_keyword = result.group(0)
                processed_commit = self.cz.process_commit(commit.message)
                changelog_entry_values[changelog_map[found_keyword]].append(
                    processed_commit
                )
                break

        changelog_str += f"\n## {changelog_entry_key}\n"
        for key, values in changelog_entry_values.items():
            if not values:
                continue
            changelog_str += f"* {key}\n"
            for value in values:
                changelog_str += f"    * {value}\n"

        with open(self.file_name, "w") as changelog_file:
            changelog_file.write(changelog_str)
