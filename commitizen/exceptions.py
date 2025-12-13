from __future__ import annotations

from enum import IntEnum
from typing import Any

from commitizen import out


class ExitCode(IntEnum):
    EXPECTED_EXIT = 0
    NO_COMMITIZEN_FOUND = 1
    NOT_A_GIT_PROJECT = 2
    NO_COMMITS_FOUND = 3
    NO_VERSION_SPECIFIED = 4
    NO_PATTERN_MAP = 5
    BUMP_COMMIT_FAILED = 6
    BUMP_TAG_FAILED = 7
    NO_ANSWERS = 8
    COMMIT_ERROR = 9
    NO_COMMIT_BACKUP = 10
    NOTHING_TO_COMMIT = 11
    CUSTOM_ERROR = 12
    NO_COMMAND_FOUND = 13
    INVALID_COMMIT_MSG = 14
    MISSING_CZ_CUSTOMIZE_CONFIG = 15
    NO_REVISION = 16
    CURRENT_VERSION_NOT_FOUND = 17
    INVALID_COMMAND_ARGUMENT = 18
    INVALID_CONFIGURATION = 19
    NOT_ALLOWED = 20
    NO_INCREMENT = 21
    CHARACTER_SET_DECODE_ERROR = 22
    GIT_COMMAND_ERROR = 23
    INVALID_MANUAL_VERSION = 24
    INIT_FAILED = 25
    RUN_HOOK_FAILED = 26
    VERSION_PROVIDER_UNKNOWN = 27
    VERSION_SCHEME_UNKNOWN = 28
    CHANGELOG_FORMAT_UNKNOWN = 29
    CONFIG_FILE_NOT_FOUND = 30
    CONFIG_FILE_IS_EMPTY = 31
    COMMIT_MESSAGE_LENGTH_LIMIT_EXCEEDED = 32

    @classmethod
    def from_str(cls, value: str) -> ExitCode:
        if value.isdecimal():
            return cls(int(value))
        return cls[value.strip()]


class CommitizenException(Exception):
    def __init__(self, *args: str, **kwargs: Any) -> None:
        self.output_method = kwargs.get("output_method") or out.error
        self.exit_code: ExitCode = self.__class__.exit_code
        if args:
            self.message = args[0]
        elif hasattr(self.__class__, "message"):
            self.message = self.__class__.message
        else:
            self.message = ""

    def __str__(self) -> str:
        return self.message


class ExpectedExit(CommitizenException):
    exit_code = ExitCode.EXPECTED_EXIT

    def __init__(self, *args: str, **kwargs: Any) -> None:
        kwargs["output_method"] = kwargs.get("output_method") or out.write
        super().__init__(*args, **kwargs)


class DryRunExit(ExpectedExit):
    """Exit due to passing `--dry-run` option"""


class NoneIncrementExit(CommitizenException):
    """The commits found are not eligible to be bumped"""

    exit_code = ExitCode.NO_INCREMENT


class NoCommitizenFoundException(CommitizenException):
    """Using a cz (e.g., `cz_jira`) that cannot be found in your system"""

    exit_code = ExitCode.NO_COMMITIZEN_FOUND


class NotAGitProjectError(CommitizenException):
    """Not in a git project"""

    exit_code = ExitCode.NOT_A_GIT_PROJECT
    message = "fatal: not a git repository (or any of the parent directories): .git"


class MissingCzCustomizeConfigError(CommitizenException):
    """Configuration is missing for `cz_customize`"""

    exit_code = ExitCode.MISSING_CZ_CUSTOMIZE_CONFIG
    message = "fatal: customize is not set in configuration file."


class NoCommitsFoundError(CommitizenException):
    """No commits found"""

    exit_code = ExitCode.NO_COMMITS_FOUND


class NoVersionSpecifiedError(CommitizenException):
    """Version is not specified in configuration file"""

    exit_code = ExitCode.NO_VERSION_SPECIFIED
    message = (
        "[NO_VERSION_SPECIFIED]\n"
        "Check if current version is specified in config file, like:\n"
        "version = 0.4.3\n"
    )


class NoPatternMapError(CommitizenException):
    """bump / changelog pattern or map can not be found in configuration file"""

    exit_code = ExitCode.NO_PATTERN_MAP


class BumpCommitFailedError(CommitizenException):
    """Commit failed when bumping version"""

    exit_code = ExitCode.BUMP_COMMIT_FAILED


class BumpTagFailedError(CommitizenException):
    """Tag failed when bumping version"""

    exit_code = ExitCode.BUMP_TAG_FAILED


class CurrentVersionNotFoundError(CommitizenException):
    """Current version cannot be found in `version_files`"""

    exit_code = ExitCode.CURRENT_VERSION_NOT_FOUND


class NoAnswersError(CommitizenException):
    """No user response given"""

    exit_code = ExitCode.NO_ANSWERS


class CommitError(CommitizenException):
    """git commit error"""

    exit_code = ExitCode.COMMIT_ERROR


class NoCommitBackupError(CommitizenException):
    """Commit backup file is not found"""

    exit_code = ExitCode.NO_COMMIT_BACKUP
    message = "No commit backup found"


class NothingToCommitError(CommitizenException):
    """Nothing in staging to be committed"""

    exit_code = ExitCode.NOTHING_TO_COMMIT


class CustomError(CommitizenException):
    """`CzException` raised"""

    exit_code = ExitCode.CUSTOM_ERROR


class InvalidCommitMessageError(CommitizenException):
    """The commit message does not pass `cz check`"""

    exit_code = ExitCode.INVALID_COMMIT_MSG


class NoRevisionError(CommitizenException):
    """No revision found"""

    exit_code = ExitCode.NO_REVISION
    message = "No tag found to do an incremental changelog"


class NoCommandFoundError(CommitizenException):
    """No command found when running Commitizen cli (e.g., `cz --debug`)"""

    exit_code = ExitCode.NO_COMMAND_FOUND
    message = "Command is required"


class InvalidCommandArgumentError(CommitizenException):
    """The argument provided to the command is invalid (e.g. `cz check -commit-msg-file filename --rev-range master..`)"""

    exit_code = ExitCode.INVALID_COMMAND_ARGUMENT


class InvalidConfigurationError(CommitizenException):
    """An error was found in the Commitizen Configuration, such as duplicates in `change_type_order`"""

    exit_code = ExitCode.INVALID_CONFIGURATION


class NotAllowed(CommitizenException):
    """`--incremental` cannot be combined with a `rev_range`"""

    exit_code = ExitCode.NOT_ALLOWED


class CharacterSetDecodeError(CommitizenException):
    """The character encoding of the command output could not be determined"""

    exit_code = ExitCode.CHARACTER_SET_DECODE_ERROR


class GitCommandError(CommitizenException):
    """Unexpected failure while calling a git command"""

    exit_code = ExitCode.GIT_COMMAND_ERROR


class InvalidManualVersion(CommitizenException):
    """Manually provided version is invalid"""

    exit_code = ExitCode.INVALID_MANUAL_VERSION


class InitFailedError(CommitizenException):
    """Failed to initialize pre-commit"""

    exit_code = ExitCode.INIT_FAILED


class RunHookError(CommitizenException):
    """An error occurred during a hook execution"""

    exit_code = ExitCode.RUN_HOOK_FAILED


class VersionProviderUnknown(CommitizenException):
    """Unknown `version_provider`"""

    exit_code = ExitCode.VERSION_PROVIDER_UNKNOWN


class VersionSchemeUnknown(CommitizenException):
    """Unknown `version_scheme`"""

    exit_code = ExitCode.VERSION_SCHEME_UNKNOWN


class ChangelogFormatUnknown(CommitizenException):
    """Unknown `changelog_format` or cannot be determined by the file extension"""

    exit_code = ExitCode.CHANGELOG_FORMAT_UNKNOWN
    message = "Unknown changelog format identifier"


class ConfigFileNotFound(CommitizenException):
    """The configuration file is not found"""

    exit_code = ExitCode.CONFIG_FILE_NOT_FOUND
    message = "Cannot found the config file, please check your file path again."


class ConfigFileIsEmpty(CommitizenException):
    """The configuration file is empty"""

    exit_code = ExitCode.CONFIG_FILE_IS_EMPTY
    message = "Config file is empty, please check your file path again."


class CommitMessageLengthExceededError(CommitizenException):
    """The commit message length exceeds the given limit."""

    exit_code = ExitCode.COMMIT_MESSAGE_LENGTH_LIMIT_EXCEEDED
    message = "Length of commit message exceeds the given limit."


# When adding / updating a new exit code, please update the documentation of the exit codes in docs/exit_codes.md
