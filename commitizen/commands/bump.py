from __future__ import annotations

import warnings
from logging import getLogger
from typing import cast

import questionary

from commitizen import bump, factory, git, hooks, out
from commitizen.changelog_formats import get_changelog_format
from commitizen.commands.changelog import Changelog
from commitizen.config import BaseConfig
from commitizen.defaults import Settings
from commitizen.exceptions import (
    BumpCommitFailedError,
    BumpTagFailedError,
    DryRunExit,
    ExpectedExit,
    GetNextExit,
    InvalidManualVersion,
    NoCommitsFoundError,
    NoneIncrementExit,
    NoPatternMapError,
    NotAGitProjectError,
    NotAllowed,
    NoVersionSpecifiedError,
)
from commitizen.providers import get_provider
from commitizen.tags import TagRules
from commitizen.version_schemes import (
    Increment,
    InvalidVersion,
    Prerelease,
    get_version_scheme,
)

logger = getLogger("commitizen")


class Bump:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: BaseConfig, arguments: dict):
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.encoding = config.settings["encoding"]
        self.arguments: dict = arguments
        self.bump_settings: dict = {
            **config.settings,
            **{
                key: arguments[key]
                for key in [
                    "tag_format",
                    "prerelease",
                    "increment",
                    "increment_mode",
                    "bump_message",
                    "gpg_sign",
                    "annotated_tag",
                    "annotated_tag_message",
                    "major_version_zero",
                    "prerelease_offset",
                    "template",
                    "file_name",
                ]
                if arguments[key] is not None
            },
        }
        self.cz = factory.commiter_factory(self.config)
        self.changelog_flag = arguments["changelog"]
        self.changelog_config = self.config.settings.get("update_changelog_on_bump")
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
            self.config.settings, arguments["version_scheme"] or deprecated_version_type
        )
        self.file_name = arguments["file_name"] or self.config.settings.get(
            "changelog_file"
        )
        self.changelog_format = get_changelog_format(self.config, self.file_name)

        self.template = (
            arguments["template"]
            or self.config.settings.get("template")
            or self.changelog_format.template
        )
        self.extras = arguments["extras"]

    def is_initial_tag(
        self, current_tag: git.GitTag | None, is_yes: bool = False
    ) -> bool:
        """Check if reading the whole git tree up to HEAD is needed."""
        is_initial = False
        if not current_tag:
            if is_yes:
                is_initial = True
            else:
                out.info("No tag matching configuration could not be found.")
                out.info(
                    "Possible causes:\n"
                    "- version in configuration is not the current version\n"
                    "- tag_format or legacy_tag_formats is missing, check them using 'git tag --list'\n"
                )
                is_initial = questionary.confirm("Is this the first tag created?").ask()
        return is_initial

    def find_increment(self, commits: list[git.GitCommit]) -> Increment | None:
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

    def __call__(self) -> None:  # noqa: C901
        """Steps executed to bump."""
        provider = get_provider(self.config)

        try:
            current_version = self.scheme(provider.get_version())
        except TypeError:
            raise NoVersionSpecifiedError()

        bump_commit_message: str = self.bump_settings["bump_message"]
        version_files: list[str] = self.bump_settings["version_files"]
        major_version_zero: bool = self.bump_settings["major_version_zero"]
        prerelease_offset: int = self.bump_settings["prerelease_offset"]

        dry_run: bool = self.arguments["dry_run"]
        is_yes: bool = self.arguments["yes"]
        increment: Increment | None = self.arguments["increment"]
        prerelease: Prerelease | None = self.arguments["prerelease"]
        devrelease: int | None = self.arguments["devrelease"]
        is_files_only: bool | None = self.arguments["files_only"]
        is_local_version: bool = self.arguments["local_version"]
        manual_version = self.arguments["manual_version"]
        build_metadata = self.arguments["build_metadata"]
        increment_mode: str = self.arguments["increment_mode"]
        get_next: bool = self.arguments["get_next"]
        allow_no_commit: bool | None = self.arguments["allow_no_commit"]

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

            if build_metadata:
                raise NotAllowed(
                    "--build-metadata cannot be combined with MANUAL_VERSION"
                )

            if major_version_zero:
                raise NotAllowed(
                    "--major-version-zero cannot be combined with MANUAL_VERSION"
                )

            if get_next:
                raise NotAllowed("--get-next cannot be combined with MANUAL_VERSION")

        if major_version_zero:
            if not current_version.release[0] == 0:
                raise NotAllowed(
                    f"--major-version-zero is meaningless for current version {current_version}"
                )

        if build_metadata:
            if is_local_version:
                raise NotAllowed(
                    "--local-version cannot be combined with --build-metadata"
                )

        if get_next:
            # if trying to use --get-next, we should not allow --changelog or --changelog-to-stdout
            if self.changelog_flag or bool(self.changelog_to_stdout):
                raise NotAllowed(
                    "--changelog or --changelog-to-stdout is not allowed with --get-next"
                )
            # --get-next is a special case, taking precedence over config for 'update_changelog_on_bump'
            self.changelog_config = False
            # Setting dry_run to prevent any unwanted changes to the repo or files
            self.dry_run = True
        else:
            # If user specified changelog_to_stdout, they probably want the
            # changelog to be generated as well, this is the most intuitive solution
            self.changelog_flag = (
                self.changelog_flag
                or bool(self.changelog_to_stdout)
                or self.changelog_config
            )

        rules = TagRules.from_settings(cast(Settings, self.bump_settings))
        current_tag = rules.find_tag_for(git.get_tags(), current_version)
        current_tag_version = getattr(
            current_tag, "name", rules.normalize_tag(current_version)
        )

        is_initial = self.is_initial_tag(current_tag, is_yes)

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
                if current_tag:
                    commits = git.get_commits(current_tag.name)
                else:
                    commits = git.get_commits()

                # No commits, there is no need to create an empty tag.
                # Unless we previously had a prerelease.
                if (
                    not commits
                    and not current_version.is_prerelease
                    and not allow_no_commit
                ):
                    raise NoCommitsFoundError(
                        "[NO_COMMITS_FOUND]\nNo new commits found."
                    )

                increment = self.find_increment(commits)

            # It may happen that there are commits, but they are not eligible
            # for an increment, this generates a problem when using prerelease (#281)
            if prerelease and increment is None and not current_version.is_prerelease:
                raise NoCommitsFoundError(
                    "[NO_COMMITS_FOUND]\n"
                    "No commits found to generate a pre-release.\n"
                    "To avoid this error, manually specify the type of increment with `--increment`"
                )

            # we create an empty PATCH increment for empty tag
            if increment is None and allow_no_commit:
                increment = "PATCH"

            new_version = current_version.bump(
                increment,
                prerelease=prerelease,
                prerelease_offset=prerelease_offset,
                devrelease=devrelease,
                is_local_version=is_local_version,
                build_metadata=build_metadata,
                exact_increment=increment_mode == "exact",
            )

        new_tag_version = rules.normalize_tag(new_version)
        message = bump.create_commit_message(
            current_version, new_version, bump_commit_message
        )

        if get_next:
            if increment is None and new_tag_version == current_tag_version:
                raise NoneIncrementExit(
                    "[NO_COMMITS_TO_BUMP]\n"
                    "The commits found are not eligible to be bumped"
                )

            out.write(str(new_version))
            raise GetNextExit()

        # Report found information
        information = f"{message}\ntag to create: {new_tag_version}\n"
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
                "[NO_COMMITS_TO_BUMP]\nThe commits found are not eligible to be bumped"
            )

        files: list[str] = []
        if self.changelog_flag:
            args = {
                "unreleased_version": new_tag_version,
                "template": self.template,
                "extras": self.extras,
                "incremental": True,
                "dry_run": dry_run,
            }
            if self.changelog_to_stdout:
                changelog_cmd = Changelog(self.config, {**args, "dry_run": True})
                try:
                    changelog_cmd()
                except DryRunExit:
                    pass

            args["file_name"] = self.file_name
            changelog_cmd = Changelog(self.config, args)
            changelog_cmd()
            files.append(changelog_cmd.file_name)

        # Do not perform operations over files or git.
        if dry_run:
            raise DryRunExit()

        files.extend(
            bump.update_version_in_files(
                str(current_version),
                str(new_version),
                version_files,
                check_consistency=self.check_consistency,
                encoding=self.encoding,
            )
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
                changelog_file_name=changelog_cmd.file_name
                if self.changelog_flag
                else None,
            )

        if is_files_only:
            raise ExpectedExit()

        # FIXME: check if any changes have been staged
        git.add(*files)
        c = git.commit(message, args=self._get_commit_args())
        if self.retry and c.return_code != 0 and self.changelog_flag:
            # Maybe pre-commit reformatted some files? Retry once
            logger.debug("1st git.commit error: %s", c.err)
            logger.info("1st commit attempt failed; retrying once")
            git.add(*files)
            c = git.commit(message, args=self._get_commit_args())
        if c.return_code != 0:
            err = c.err.strip() or c.out
            raise BumpCommitFailedError(f'2nd git.commit error: "{err}"')

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
            or bool(self.config.settings.get("annotated_tag", False))
            or bool(self.bump_settings.get("annotated_tag_message", False)),
            msg=self.bump_settings.get("annotated_tag_message", None),
            # TODO: also get from self.config.settings?
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
                changelog_file_name=changelog_cmd.file_name
                if self.changelog_flag
                else None,
            )

        # TODO: For v3 output this only as diagnostic and remove this if
        if self.changelog_to_stdout:
            out.diagnostic("Done!")
        else:
            out.success("Done!")

    def _get_commit_args(self) -> str:
        commit_args = ["-a"]
        if self.no_verify:
            commit_args.append("--no-verify")
        return " ".join(commit_args)
