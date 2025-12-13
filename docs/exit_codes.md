# Exit Codes

Commitizen handles expected exceptions through `CommitizenException` and returns different exit codes for different situations. This reference is useful when you need to ignore specific errors in your CI/CD pipeline or automation scripts.

All exit codes are defined in [commitizen/exceptions.py](https://github.com/commitizen-tools/commitizen/blob/master/commitizen/exceptions.py).

## Exit Code Reference

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

## Ignoring Exit Codes

In some scenarios, you may want Commitizen to continue execution even when certain errors occur. This is particularly useful in CI/CD pipelines where you want to handle specific errors gracefully.

### Using `--no-raise` Flag

The `--no-raise` (or `-nr`) flag allows you to specify exit codes that should not cause Commitizen to exit with an error. You can use either:

- **Exit code numbers**: `21`, `3`, `4`
- **Exit code names**: `NO_INCREMENT`, `NO_COMMITS_FOUND`, `NO_VERSION_SPECIFIED`
- **Mixed format**: `21,NO_COMMITS_FOUND,4`

Multiple exit codes can be specified as a comma-separated list.

### Common Use Cases

#### Ignoring No Increment Errors

The most common use case is to ignore `NoneIncrementExit` (exit code 21) when running `cz bump`. This allows the command to succeed even when no commits are eligible for a version bump:

```sh
cz -nr 21 bump
```

Or using the exit code name:

```sh
cz -nr NO_INCREMENT bump
```

This is useful in CI pipelines where you want to run `cz bump` regularly, but don't want the pipeline to fail when there are no version-worthy commits.

#### Ignoring Multiple Exit Codes

You can ignore multiple exit codes at once:

```sh
cz --no-raise 21,3,4 bump
```

This example ignores:

- `21` (`NoneIncrementExit`) - No eligible commits for bump
- `3` (`NoCommitsFoundError`) - No commits found
- `4` (`NoVersionSpecifiedError`) - Version not specified

### Finding the Exit Code

If you encounter an error and want to ignore it, you can find the exit code in two ways:

#### Method 1: Check the Exit Code After Running

After running a Commitizen command that fails, check the exit code:

```sh
cz bump
echo $?  # Prints the exit code (e.g., 21)
```

Then use that exit code with `--no-raise`:

```sh
cz -nr 21 bump
```

#### Method 2: Look Up the Exception

1. Check the error message to identify the exception type
2. Find the corresponding exit code in the table above
3. Use that exit code with `--no-raise`

For example, if you see `NoneIncrementExit` in the error, look it up in the table to find it's exit code 21, then use:

```sh
cz -nr 21 bump
```

### Best Practices

- **Document your usage**: If you use `--no-raise` in scripts or CI/CD, document why specific exit codes are ignored
- **Be specific**: Only ignore exit codes you understand and have a reason to ignore
- **Test thoroughly**: Ensure that ignoring certain exit codes doesn't mask real problems in your workflow
- **Use exit code names**: When possible, use exit code names (e.g., `NO_INCREMENT`) instead of numbers for better readability

### Example: CI/CD Pipeline

Here's an example of using `--no-raise` in a CI/CD pipeline:

```yaml
# .github/workflows/release.yml
- name: Bump version
  run: |
    cz -nr NO_INCREMENT bump || true
    # Continue even if no version bump is needed
```

This ensures the pipeline continues even when there are no commits eligible for a version bump.
