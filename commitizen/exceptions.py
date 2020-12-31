import enum

from commitizen import out


class ExitCode(enum.IntEnum):
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


class CommitizenException(Exception):
    def __init__(self, *args, **kwargs):
        self.output_method = kwargs.get("output_method") or out.error
        self.exit_code = self.__class__.exit_code
        if args:
            self.message = args[0]
        elif hasattr(self.__class__, "message"):
            self.message = self.__class__.message
        else:
            self.message = ""

    def __str__(self):
        return self.message


class ExpectedExit(CommitizenException):
    exit_code = ExitCode.EXPECTED_EXIT

    def __init__(self, *args, **kwargs):
        output_method = kwargs.get("output_method") or out.write
        kwargs["output_method"] = output_method
        super().__init__(*args, **kwargs)


class DryRunExit(ExpectedExit):
    pass


class NoneIncrementExit(ExpectedExit):
    pass


class NoCommitizenFoundException(CommitizenException):
    exit_code = ExitCode.NO_COMMITIZEN_FOUND


class NotAGitProjectError(CommitizenException):
    exit_code = ExitCode.NOT_A_GIT_PROJECT
    message = "fatal: not a git repository (or any of the parent directories): .git"


class MissingCzCustomizeConfigError(CommitizenException):
    exit_code = ExitCode.MISSING_CZ_CUSTOMIZE_CONFIG
    message = "fatal: customize is not set in configuration file."


class NoCommitsFoundError(CommitizenException):
    exit_code = ExitCode.NO_COMMITS_FOUND


class NoVersionSpecifiedError(CommitizenException):
    exit_code = ExitCode.NO_VERSION_SPECIFIED
    message = (
        "[NO_VERSION_SPECIFIED]\n"
        "Check if current version is specified in config file, like:\n"
        "version = 0.4.3\n"
    )


class NoPatternMapError(CommitizenException):
    exit_code = ExitCode.NO_PATTERN_MAP


class BumpCommitFailedError(CommitizenException):
    exit_code = ExitCode.BUMP_COMMIT_FAILED


class BumpTagFailedError(CommitizenException):
    exit_code = ExitCode.BUMP_TAG_FAILED


class CurrentVersionNotFoundError(CommitizenException):
    exit_code = ExitCode.CURRENT_VERSION_NOT_FOUND


class NoAnswersError(CommitizenException):
    exit_code = ExitCode.NO_ANSWERS


class CommitError(CommitizenException):
    exit_code = ExitCode.COMMIT_ERROR


class NoCommitBackupError(CommitizenException):
    exit_code = ExitCode.NO_COMMIT_BACKUP
    message = "No commit backup found"


class NothingToCommitError(CommitizenException):
    exit_code = ExitCode.NOTHING_TO_COMMIT


class CustomError(CommitizenException):
    exit_code = ExitCode.CUSTOM_ERROR


class InvalidCommitMessageError(CommitizenException):
    exit_code = ExitCode.INVALID_COMMIT_MSG


class NoRevisionError(CommitizenException):
    exit_code = ExitCode.NO_REVISION
    message = "No tag found to do an incremental changelog"


class NoCommandFoundError(CommitizenException):
    exit_code = ExitCode.NO_COMMAND_FOUND
    message = "Command is required"


class InvalidCommandArgumentError(CommitizenException):
    exit_code = ExitCode.INVALID_COMMAND_ARGUMENT


class InvalidConfigurationError(CommitizenException):
    exit_code = ExitCode.INVALID_CONFIGURATION
