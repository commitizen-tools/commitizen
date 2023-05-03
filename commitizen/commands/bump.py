from __future__ import annotations

import os
from logging import getLogger
import warnings

import questionary

from commitizen import bump, cmd, factory, git, hooks, out
from commitizen.commands.changelog import Changelog
from commitizen.config import BaseConfig
from commitizen.exceptions import (
    BumpCommitFailedError,
    BumpTagFailedError,
    DryRunExit,
    ExpectedExit,
    InvalidManualVersion,
    NoCommitsFoundError,
    NoneIncrementExit,
    NoPatternMapError,
    NotAGitProjectError,
    NotAllowed,
    NoVersionSpecifiedError,
)
from commitizen.providers import get_provider
from commitizen.version_schemes import get_version_scheme, InvalidVersion

logger = getLogger("commitizen")


class Bump:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: BaseConfig, arguments: dict):
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.arguments: dict = arguments
        self.bump_settings: dict = {
            **config.settings,
            **{
                key: arguments[key]
                for key in [
                    "tag_format",
                    "prerelease",
                    "increment",
                    "bump_message",
                    "gpg_sign",
                    "annotated_tag",
                    "major_version_zero",
                    "prerelease_offset",
                ]
                if arguments[key] is not None
            },
        }
        self.cz = factory.commiter_factory(self.config)
        self.changelog = arguments["changelog"] or self.config.settings.get(
            "update_changelog_on_bump"
        )
        self.changelog_to_stdout = arguments["changelog_to_stdout"]
        self.git_output_to_stderr = arguments["git_output_to_stderr"]
        self.no_verify = arguments["no_verify"]
        self.check_consistency = arguments["check_consistency"]
        self.retry = arguments["retry"]
        self.pre_bump_hooks = self.config.settings["pre_bump_hooks"]
        self.post_bump_hooks = self.config.settings["post_bump_hooks"]
        deprecated_version_type = arguments.get("version_type")
        if deprecated_version_type:
            warnings.warn(
                DeprecationWarning(
                    "`--version-type` parameter is deprecated and will be removed in commitizen 4. "
                    "Please use `--version-scheme` instead"
                )
            )
        self.scheme = get_version_scheme(
            self.config, arguments["version_scheme"] or deprecated_version_type
        )

    def is_initial_tag(self, current_tag_version: str, is_yes: bool = False) -> bool:
        """Check if reading the whole git tree up to HEAD is needed."""
        is_initial = False
        if not git.tag_exist(current_tag_version):
            if is_yes:
                is_initial = True
            else:
                out.info(f"Tag {current_tag_version} could not be found. ")
                out.info(
                    (
                        "Possible causes:\n"
                        "- version in configuration is not the current version\n"
                        "- tag_format is missing, check them using 'git tag --list'\n"
                    )
                )
                is_initial = questionary.confirm("Is this the first tag created?").ask()
        return is_initial

    def find_increment(self, commits: list[git.GitCommit]) -> str | None:
        # Update the bump map to ensure major version doesn't increment.
        is_major_version_zero: bool = self.bump_settings["major_version_zero"]
        # self.cz.bump_map = defaults.bump_map_major_version_zero
        bump_map = (
            self.cz.bump_map_major_version_zero
            if is_major_version_zero
            else self.cz.bump_map
        )
        bump_pattern = self.cz.bump_pattern

        if not bump_map or not bump_pattern:
            raise NoPatternMapError(
                f"'{self.config.settings['name']}' rule does not support bump"
            )
        increment = bump.find_increment(
            commits, regex=bump_pattern, increments_map=bump_map
        )
        return increment

    def __call__(self):  # noqa: C901
        """Steps executed to bump."""
        provider = get_provider(self.config)

        try:
            current_version = self.scheme(provider.get_version())
        except TypeError:
            raise NoVersionSpecifiedError()

        tag_format: str = self.bump_settings["tag_format"]
        bump_commit_message: str = self.bump_settings["bump_message"]
        version_files: list[str] = self.bump_settings["version_files"]
        major_version_zero: bool = self.bump_settings["major_version_zero"]
        prerelease_offset: int = self.bump_settings["prerelease_offset"]

        dry_run: bool = self.arguments["dry_run"]
        is_yes: bool = self.arguments["yes"]
        increment: str | None = self.arguments["increment"]
        prerelease: str | None = self.arguments["prerelease"]
        devrelease: int | None = self.arguments["devrelease"]
        is_files_only: bool | None = self.arguments["files_only"]
        is_local_version: bool | None = self.arguments["local_version"]
        manual_version = self.arguments["manual_version"]

        if manual_version:
            if increment:
                raise NotAllowed("--increment cannot be combined with MANUAL_VERSION")

            if prerelease:
                raise NotAllowed("--prerelease cannot be combined with MANUAL_VERSION")

            if devrelease is not None:
                raise NotAllowed("--devrelease cannot be combined with MANUAL_VERSION")

            if is_local_version:
                raise NotAllowed(
                    "--local-version cannot be combined with MANUAL_VERSION"
                )

            if major_version_zero:
                raise NotAllowed(
                    "--major-version-zero cannot be combined with MANUAL_VERSION"
                )

            if prerelease_offset:
                raise NotAllowed(
                    "--prerelease-offset cannot be combined with MANUAL_VERSION"
                )

        if major_version_zero:
            if not current_version.release[0] == 0:
                raise NotAllowed(
                    f"--major-version-zero is meaningless for current version {current_version}"
                )

        current_tag_version: str = bump.normalize_tag(
            current_version,
            tag_format=tag_format,
            scheme=self.scheme,
        )

        is_initial = self.is_initial_tag(current_tag_version, is_yes)
        if is_initial:
            commits = git.get_commits()
        else:
            commits = git.get_commits(current_tag_version)

        # If user specified changelog_to_stdout, they probably want the
        # changelog to be generated as well, this is the most intuitive solution
        if not self.changelog and self.changelog_to_stdout:
            self.changelog = True

        # No commits, there is no need to create an empty tag.
        # Unless we previously had a prerelease.
        if not commits and not current_version.is_prerelease:
            raise NoCommitsFoundError("[NO_COMMITS_FOUND]\n" "No new commits found.")

        if manual_version:
            try:
                new_version = self.scheme(manual_version)
            except InvalidVersion as exc:
                raise InvalidManualVersion(
                    "[INVALID_MANUAL_VERSION]\n"
                    f"Invalid manual version: '{manual_version}'"
                ) from exc
        else:
            if increment is None:
                increment = self.find_increment(commits)

            # It may happen that there are commits, but they are not eligible
            # for an increment, this generates a problem when using prerelease (#281)
            if prerelease and increment is None and not current_version.is_prerelease:
                raise NoCommitsFoundError(
                    "[NO_COMMITS_FOUND]\n"
                    "No commits found to generate a pre-release.\n"
                    "To avoid this error, manually specify the type of increment with `--increment`"
                )

            # Increment is removed when current and next version
            # are expected to be prereleases.
            if prerelease and current_version.is_prerelease:
                increment = None

            new_version = current_version.bump(
                increment,
                prerelease=prerelease,
                prerelease_offset=prerelease_offset,
                devrelease=devrelease,
                is_local_version=is_local_version,
            )

        new_tag_version = bump.normalize_tag(
            new_version,
            tag_format=tag_format,
            scheme=self.scheme,
        )
        message = bump.create_commit_message(
            current_version, new_version, bump_commit_message
        )

        # Report found information
        information = f"{message}\n" f"tag to create: {new_tag_version}\n"
        if increment:
            information += f"increment detected: {increment}\n"

        if self.changelog_to_stdout:
            # When the changelog goes to stdout, we want to send
            # the bump information to stderr, this way the
            # changelog output can be captured
            out.diagnostic(information)
        else:
            out.write(information)

        if increment is None and new_tag_version == current_tag_version:
            raise NoneIncrementExit(
                "[NO_COMMITS_TO_BUMP]\n"
                "The commits found are not eligible to be bumped"
            )

        if self.changelog:
            if self.changelog_to_stdout:
                changelog_cmd = Changelog(
                    self.config,
                    {
                        "unreleased_version": new_tag_version,
                        "incremental": True,
                        "dry_run": True,
                    },
                )
                try:
                    changelog_cmd()
                except DryRunExit:
                    pass
            changelog_cmd = Changelog(
                self.config,
                {
                    "unreleased_version": new_tag_version,
                    "incremental": True,
                    "dry_run": dry_run,
                },
            )
            changelog_cmd()
            file_names = []
            for file_name in version_files:
                drive, tail = os.path.splitdrive(file_name)
                path, _, regex = tail.partition(":")
                path = drive + path if path != "" else drive + regex
                file_names.append(path)
            git_add_changelog_and_version_files_command = (
                f"git add {changelog_cmd.file_name} "
                f"{' '.join(name for name in file_names)}"
            )
            c = cmd.run(git_add_changelog_and_version_files_command)

        # Do not perform operations over files or git.
        if dry_run:
            raise DryRunExit()

        bump.update_version_in_files(
            str(current_version),
            str(new_version),
            version_files,
            check_consistency=self.check_consistency,
        )

        provider.set_version(str(new_version))

        if self.pre_bump_hooks:
            hooks.run(
                self.pre_bump_hooks,
                _env_prefix="CZ_PRE_",
                is_initial=is_initial,
                current_version=str(current_version),
                current_tag_version=current_tag_version,
                new_version=new_version.public,
                new_tag_version=new_tag_version,
                message=message,
                increment=increment,
                changelog_file_name=changelog_cmd.file_name if self.changelog else None,
            )

        if is_files_only:
            raise ExpectedExit()

        c = git.commit(message, args=self._get_commit_args())
        if self.retry and c.return_code != 0 and self.changelog:
            # Maybe pre-commit reformatted some files? Retry once
            logger.debug("1st git.commit error: %s", c.err)
            logger.info("1st commit attempt failed; retrying once")
            cmd.run(git_add_changelog_and_version_files_command)
            c = git.commit(message, args=self._get_commit_args())
        if c.return_code != 0:
            raise BumpCommitFailedError(f'2nd git.commit error: "{c.err.strip()}"')

        if c.out:
            if self.git_output_to_stderr:
                out.diagnostic(c.out)
            else:
                out.write(c.out)
        if c.err:
            if self.git_output_to_stderr:
                out.diagnostic(c.err)
            else:
                out.write(c.err)

        c = git.tag(
            new_tag_version,
            signed=self.bump_settings.get("gpg_sign", False)
            or bool(self.config.settings.get("gpg_sign", False)),
            annotated=self.bump_settings.get("annotated_tag", False)
            or bool(self.config.settings.get("annotated_tag", False)),
        )
        if c.return_code != 0:
            raise BumpTagFailedError(c.err)

        if self.post_bump_hooks:
            hooks.run(
                self.post_bump_hooks,
                _env_prefix="CZ_POST_",
                was_initial=is_initial,
                previous_version=str(current_version),
                previous_tag_version=current_tag_version,
                current_version=new_version.public,
                current_tag_version=new_tag_version,
                message=message,
                increment=increment,
                changelog_file_name=changelog_cmd.file_name if self.changelog else None,
            )

        # TODO: For v3 output this only as diagnostic and remove this if
        if self.changelog_to_stdout:
            out.diagnostic("Done!")
        else:
            out.success("Done!")

    def _get_commit_args(self):
        commit_args = ["-a"]
        if self.no_verify:
            commit_args.append("--no-verify")
        return " ".join(commit_args)
