import enum

from commitizen import out


class ExitCode(enum.IntEnum):
    NO_COMMITIZEN_FOUND = 1

    NOT_A_GIT_PROJECT = 2
    MISSING_CONFIG = 15

    NO_COMMITS_FOUND = 3
    NO_VERSION_SPECIFIED = 4
    NO_PATTERN_MAP = 5
    COMMIT_FAILED = 6
    TAG_FAILED = 7
    CURRENT_VERSION_NOT_FOUND = 17

    NO_ANSWERS = 8
    COMMIT_ERROR = 9
    NO_COMMIT_BACKUP = 10
    NOTHING_TO_COMMIT = 11
    CUSTOM_ERROR = 12

    INVALID_COMMIT_MSG = 14

    # Changelog
    NO_REVISION = 16


class CommitizenException(Exception):
    pass


class NoCommitizenFoundException(CommitizenException):
    exit_code = ExitCode.NO_COMMITIZEN_FOUND


class NotAGitProjectError(CommitizenException):
    exit_code = ExitCode.NOT_A_GIT_PROJECT

    def __init__(self, *args, **kwargs):
        out.error(
            "fatal: not a git repository (or any of the parent directories): .git"
        )


class MissingConfigError(CommitizenException):
    exit_code = ExitCode.MISSING_CONFIG

    def __init__(self, *args, **kwargs):
        out.error("fatal: customize is not set in configuration file.")


class NoCommitsFoundError(CommitizenException):
    exit_code = ExitCode.NO_COMMITS_FOUND


class NoVersionSpecifiedError(CommitizenException):
    exit_code = ExitCode.NO_VERSION_SPECIFIED


class NoPatternMapError(CommitizenException):
    exit_code = ExitCode.NO_PATTERN_MAP


class CommitFailedError(CommitizenException):
    exit_code = ExitCode.COMMIT_FAILED


class TagFailedError(CommitizenException):
    exit_code = ExitCode.TAG_FAILED


class CurrentVersionNotFoundError(CommitizenException):
    exit_code = ExitCode.CURRENT_VERSION_NOT_FOUND


class NoAnswersError(CommitizenException):
    exit_code = ExitCode.NO_ANSWERS


class CommitError(CommitizenException):
    exit_code = ExitCode.COMMIT_ERROR


class NoCommitBackupError(CommitizenException):
    exit_code = ExitCode.NO_COMMIT_BACKUP


class NothingToCommitError(CommitizenException):
    exit_code = ExitCode.NOTHING_TO_COMMIT


class CustomError(CommitizenException):
    exit_code = ExitCode.CUSTOM_ERROR


class InvalidCommitMessageError(CommitizenException):
    exit_code = ExitCode.INVALID_COMMIT_MSG


class NoRevisionError(CommitizenException):
    exit_code = ExitCode.NO_REVISION
