# Exit Codes

Commitizen handles expected exceptions through `CommitizenException` and returns different exit codes for different situations. They could be useful if you want to ignore specific errors in your pipeline.

These exit codes can be found in `commitizen/exceptions.py::ExitCode`.

| Exception                   | Exit Code | Description                                                                                                 |
| --------------------------- | --------- | ----------------------------------------------------------------------------------------------------------- |
| ExpectedExit                | 0         | Expected exit                                                                                               |
| DryRunExit                  | 0         | Exit due to passing `--dry-run` option                                                                      |
| NoCommitizenFoundException  | 1         | Using a cz (e.g., `cz_jira`) that cannot be found in your system                                            |
| NotAGitProjectError         | 2         | Not in a git project                                                                                        |
| NoCommitsFoundError         | 3         | No commit found                                                                                             |
| NoVersionSpecifiedError     | 4         | Version can not be found in configuration file                                                              |
| NoPatternMapError           | 5         | bump / changelog pattern or map can not be found in configuration file                                      |
| BumpCommitFailedError       | 6         | Commit error when bumping version                                                                           |
| BumpTagFailedError          | 7         | Tag error when bumping version                                                                              |
| NoAnswersError              | 8         | No user response given                                                                                      |
| CommitError                 | 9         | git commit error                                                                                            |
| NoCommitBackupError         | 10        | Commit back up file cannot be found                                                                         |
| NothingToCommitError        | 11        | Nothing in staging to be committed                                                                          |
| CustomError                 | 12        | `CzException` raised                                                                                        |
| NoCommandFoundError         | 13        | No command found when running commitizen cli (e.g., `cz --debug`)                                           |
| InvalidCommitMessageError   | 14        | The commit message does not pass `cz check`                                                                 |
| MissingConfigError          | 15        | Configuration missed for `cz_customize`                                                                     |
| NoRevisionError             | 16        | No revision found                                                                                           |
| CurrentVersionNotFoundError | 17        | current version cannot be found in _version_files_                                                          |
| InvalidCommandArgumentError | 18        | The argument provide to command is invalid (e.g. `cz check -commit-msg-file filename --rev-range master..`) |
| InvalidConfigurationError   | 19        | An error was found in the Commitizen Configuration, such as duplicates in `change_type_order`               |
| NotAllowed                  | 20        | `--incremental` cannot be combined with a `rev_range`                                                       |
| NoneIncrementExit           | 21        | The commits found are not eligible to be bumped                                                             |
| CharacterSetDecodeError     | 22        | The character encoding of the command output could not be determined                                        |
| GitCommandError             | 23        | Unexpected failure while calling a git command                                                              |
| InvalidManualVersion        | 24        | Manually provided version is invalid                                                                        |
| InitFailedError             | 25        | Failed to initialize pre-commit                                                                             |
| VersionProviderUnknown      | 26        | `version_provider` setting is set to an unknown version provider identifier                                |
