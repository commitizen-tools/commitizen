from packaging.version import Version
from typing import Optional

import questionary
from commitizen import bump, git, config, out, factory

NO_COMMITS_FOUND = 3
NO_VERSION_SPECIFIED = 4
NO_PATTERN_MAP = 7


class Bump:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: dict, arguments: dict):
        self.config: dict = config
        self.arguments: dict = arguments
        self.parameters: dict = {
            **config,
            **{
                key: arguments[key]
                for key in [
                    "dry_run",
                    "tag_format",
                    "prerelease",
                    "increment",
                    "bump_message",
                ]
                if arguments[key] is not None
            },
        }
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        """Steps executed to bump."""
        try:
            current_version_instance: Version = Version(self.parameters["version"])
        except TypeError:
            out.error("[NO_VERSION_SPECIFIED]")
            out.error("Check if current version is specified in config file, like:")
            out.error("version = 0.4.3")
            raise SystemExit(NO_VERSION_SPECIFIED)

        # Initialize values from sources (conf)
        current_version: str = self.config["version"]
        tag_format: str = self.parameters["tag_format"]
        bump_commit_message: str = self.parameters["bump_message"]
        current_tag_version: str = bump.create_tag(
            current_version, tag_format=tag_format
        )
        files: list = self.parameters["files"]
        dry_run: bool = self.parameters["dry_run"]

        prerelease: str = self.arguments["prerelease"]
        increment: Optional[str] = self.arguments["increment"]
        is_initial: bool = False

        # Check if reading the whole git tree up to HEAD is needed.
        if not git.tag_exist(current_tag_version):
            out.info(f"Tag {current_tag_version} could not be found. ")
            out.info(
                (
                    "Possible causes:\n"
                    "- version in configuration is not the current version\n"
                    "- tag_format is missing, check them using 'git tag --list'\n"
                )
            )
            is_initial = questionary.confirm("Is this the first tag created?").ask()

        commits = git.get_commits(current_tag_version, from_beginning=is_initial)

        # No commits, there is no need to create an empty tag.
        # Unless we previously had a prerelease.
        if not commits and not current_version_instance.is_prerelease:
            out.error("[NO_COMMITS_FOUND]")
            out.error("No new commits found.")
            raise SystemExit(NO_COMMITS_FOUND)

        if increment is None:
            bump_pattern = self.cz.bump_pattern
            bump_map = self.cz.bump_map
            if not bump_map or not bump_pattern:
                out.error(f"'{self.config['name']}' rule does not support bump")
                raise SystemExit(NO_PATTERN_MAP)
            increment = bump.find_increment(
                commits, regex=bump_pattern, increments_map=bump_map
            )

        # Increment is removed when current and next version
        # are expected to be prereleases.
        if prerelease and current_version_instance.is_prerelease:
            increment = None

        new_version = bump.generate_version(
            current_version, increment, prerelease=prerelease
        )
        new_tag_version = bump.create_tag(new_version, tag_format=tag_format)
        message = bump.create_commit_message(
            current_version, new_version, bump_commit_message
        )

        # Report found information
        out.write(message)
        out.write(f"tag to create: {new_tag_version}")
        out.write(f"increment detected: {increment}")

        # Do not perform operations over files or git.
        if dry_run:
            raise SystemExit()

        config.set_key("version", new_version.public)
        bump.update_version_in_files(current_version, new_version.public, files)
        git.commit(message, args="-a")
        git.tag(new_tag_version)
        out.success("Done!")
