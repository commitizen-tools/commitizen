import re
from collections import OrderedDict

from jinja2 import Template

from commitizen import factory, out, git, cz
from commitizen.config import BaseConfig
from commitizen.error_codes import NO_COMMITS_FOUND

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


class Changelog:
    """Generate a changelog based on the commit history."""

    def __init__(self, config: BaseConfig, args):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)

        self.file_name = args["file_name"]
        self.dry_run = args["dry_run"]
        self.start_rev = args["start_rev"]

    def __call__(self):
        changelog_map = self.cz.changelog_map
        changelog_pattern = self.cz.changelog_pattern
        if not changelog_map or not changelog_pattern:
            out.error(
                f"'{self.config.settings['name']}' rule does not support changelog"
            )

        pat = re.compile(changelog_pattern)

        commits = git.get_commits(start=self.start_rev)
        if not commits:
            raise SystemExit(NO_COMMITS_FOUND)

        tag_map = {tag.rev: tag.name for tag in git.get_tags()}

        entries = OrderedDict()
        # The latest commit is not tagged
        latest_commit = commits[0]
        if latest_commit.rev not in tag_map:
            current_key = "Unreleased"
            entries[current_key] = OrderedDict(
                {value: [] for value in changelog_map.values()}
            )
        else:
            current_key = tag_map[latest_commit.rev]

        for commit in commits:
            if commit.rev in tag_map:
                current_key = tag_map[commit.rev]
                entries[current_key] = OrderedDict(
                    {value: [] for value in changelog_map.values()}
                )

            matches = pat.match(commit.message)
            if not matches:
                continue

            processed_commit = self.cz.process_commit(commit.message)
            for group_name, commit_type in changelog_map.items():
                if matches.group(group_name):
                    entries[current_key][commit_type].append(processed_commit)
                    break

        template_file = pkg_resources.read_text(cz, "changelog_template.j2")
        jinja_template = Template(template_file)
        changelog_str = jinja_template.render(entries=entries)
        if self.dry_run:
            out.write(changelog_str)
            raise SystemExit(0)

        with open(self.file_name, "w") as changelog_file:
            changelog_file.write(changelog_str)
