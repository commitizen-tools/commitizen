# Exit Codes

Commitizen handles expected exceptions through `CommitizenException` and returns different exit codes for different situations.

The following information may come in handy if you want to ignore specific errors in your pipeline.

These exit codes can be found in [commitizen/exceptions.py](https://github.com/commitizen-tools/commitizen/blob/master/commitizen/exceptions.py).

| Exception                   | Exit Code | Description                                                                                                 |
| --------------------------- | --------- | ----------------------------------------------------------------------------------------------------------- |
| `ExpectedExit`               | 0         | Expected exit                                                                                              |
| `DryRunExit`                 | 0         | Exit due to passing `--dry-run` option                                                                    |
| `NoCommitizenFoundException` | 1         | Using a cz (e.g., `cz_jira`) that cannot be found in your system                                           |
| `NotAGitProjectError`        | 2         | Not in a git project                                                                                       |
| `NoCommitsFoundError`        | 3         | No commits found                                                                                           |
| `NoVersionSpecifiedError`    | 4         | Version is not specified in configuration file                                                             |
| `NoPatternMapError`          | 5         | bump / changelog pattern or map can not be found in configuration file                                     |
| `BumpCommitFailedError`      | 6         | Commit failed when bumping version                                                                         |
| `BumpTagFailedError`         | 7         | Tag failed when bumping version                                                                            |
| `NoAnswersError`             | 8         | No user response given                                                                                     |
| `CommitError`                | 9         | git commit error                                                                                           |
| `NoCommitBackupError`        | 10        | Commit backup file is not found                                                                            |
| `NothingToCommitError`       | 11        | Nothing in staging to be committed                                                                         |
| `CustomError`                | 12        | `CzException` raised                                                                                       |
| `NoCommandFoundError`        | 13        | No command found when running Commitizen cli (e.g., `cz --debug`)                                          |
| `InvalidCommitMessageError`  | 14        | The commit message does not pass `cz check`                                                                |
| `MissingConfigError`         | 15        | Configuration is missing for `cz_customize`                                                                |
| `NoRevisionError`            | 16        | No revision found                                                                                          |
| `CurrentVersionNotFoundError`| 17        | Current version cannot be found in `version_files`                                                         |
| `InvalidCommandArgumentError`| 18        | The argument provided to the command is invalid (e.g. `cz check -commit-msg-file filename --rev-range master..`) |
| `InvalidConfigurationError`  | 19        | An error was found in the Commitizen Configuration, such as duplicates in `change_type_order`              |
| `NotAllowed`                 | 20        | Invalid combination of command line / configuration file options                                           |
| `NoneIncrementExit`          | 21        | The commits found are not eligible to be bumped                                                            |
| `CharacterSetDecodeError`    | 22        | The character encoding of the command output could not be determined                                       |
| `GitCommandError`            | 23        | Unexpected failure while calling a git command                                                             |
| `InvalidManualVersion`       | 24        | Manually provided version is invalid                                                                       |
| `InitFailedError`            | 25        | Failed to initialize pre-commit                                                                            |
| `RunHookError`               | 26        | An error occurred during a hook execution                                                                  |
| `VersionProviderUnknown`     | 27        | Unknown `version_provider`                                                                                 |
| `VersionSchemeUnknown`       | 28        | Unknown `version_scheme`                                                                                   |
| `ChangelogFormatUnknown`     | 29        | Unknown `changelog_format` or cannot be determined by the file extension                                   |
| `ConfigFileNotFound`         | 30        | The configuration file is not found                                                                  |
| `ConfigFileIsEmpty`          | 31        | The configuration file is empty                                                                            |
| `CommitMessageLengthLimitExceededError`| 32        | The commit message length exceeds the given limit.                                               |
