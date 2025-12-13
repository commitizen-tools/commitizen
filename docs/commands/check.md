This feature checks whether a string or a range of git commits follows the given committing rules. Comments in git messages will be ignored.

To set up an automatic check before every git commit, please refer to [Automatically check message before commit](../tutorials/auto_check.md).

## Usage

![cz check --help](../images/cli_help/cz_check___help.svg)

More specifically, there are three mutually exclusive ways to use `cz check`:

- Validate a range of git commit messages with `--rev-range`
- Validate a given string with `--message` or by piping the message to it
- Validate a commit message from a file with `--commit-msg-file`

### Use `cz check` to validate a commit message before committing

#### Option 1: use `--message` to check a given string:

```bash
cz check --message <message_to_be_checked>
```

#### Option 2: pipe the message to `cz check`:
```bash
echo <message_to_be_checked> | cz check
```

#### Option 3: use `--commit-msg-file` to read the commit message from a file
```bash
cz check --commit-msg-file /path/to/file.txt
```

## Command Line Options

### `--rev-range`

Test if a given range of commits in the git log passes `cz check`.

```bash
cz check --rev-range REV_RANGE
```

For more information on `REV_RANGE`, check the [git documentation](https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection#_commit_ranges).

#### Use cases

1. Validate the latest 3 commit messages:
    ```bash
    cz check --rev-range HEAD~3..HEAD
    # or
    cz check --rev-range HEAD~3..
    # or
    cz check --rev-range HEAD~~~..
    ```

1. Validate all git commit messages on some branch up to HEAD:
    ```bash
    cz check --rev-range <branch_name>..HEAD
    ```

    For example, to check all git commit messages on `main` branch up to HEAD:
    ```bash
    cz check --rev-range main..HEAD
    ```

    or if your project still uses `master` branch:
    ```bash
    cz check --rev-range master..HEAD
    ```

    !!! note "Default branch"
        Usually the default branch is `main` or `master`.
        You can check the default branch by running `cz check --use-default-range`.

1. Validate all git commit messages starting from when you first implemented commit message linting:

    **(Why this is useful?)** Let's say you decided to enforce commit message today. However, it is impractical to `git rebase` all your previous commits. `--rev-range` helps you skip commits before you first implemented commit message linting by using a specific commit hash.

    ```bash
    cz check --rev-range <first_commit_sha>..HEAD
    ```

### `--use-default-range`

Equivalent to `--rev-range <default_branch>..HEAD`.

```bash
cz check --use-default-range
# or
cz check -d
```

### `--message`

Test if a given string passes `cz check`.

```bash
cz check --message <message_to_be_checked>
```

### `--commit-msg-file`

Test if a given file contains a commit message that passes `cz check`.

```bash
cz check --commit-msg-file <path_to_file_containing_message_to_be_checked>
```

This can be useful when cooperating with git hooks. Please check [Automatically check message before commit](../tutorials/auto_check.md) for more detailed examples.

### `--allow-abort`

Example:

```bash
cz check --message <message_to_be_checked> --allow-abort
```

Empty commit messages typically instruct Git to abort a commit, so you can pass `--allow-abort` to
permit them. Since `git commit` accepts the `--allow-empty-message` flag (primarily for wrapper scripts), you may wish to disallow such commits in CI. `--allow-abort` may be used in conjunction with any of the other options.

### `--allowed-prefixes`

Skip validation for commit messages that start with the specified prefixes.

If not set, commit messages starting with the following prefixes are ignored by `cz check`:

- `Merge`
- `Revert`
- `Pull request`
- `fixup!`
- `squash!`
- `amend!`

```bash
cz check --message <message_to_be_checked> --allowed-prefixes 'Merge' 'Revert' 'Custom Prefix'
```

For example,

```bash
# The following message passes the check because it starts with 'Merge'
cz check --message "Merge branch 'main' into feature/new-feature" --allowed-prefixes 'Merge'

# The following fails
cz check --message "Merge branch 'main' into feature/new-feature" --allowed-prefixes 'aaa'
```

### `--message-length-limit`

Restrict the length of **the first line** of the commit message.

```bash
# The following passes
cz check --message "docs(check): fix grammar issues" -l 80

# The following fails
cz check --message "docs:very long long long long message with many words" -l 3
```

By default, the limit is set to `0`, which means no limit on the length.

!!! note
    Specifically, for `ConventionalCommitsCz` the length only counts from the type of change to the subject, while the body and the footer are not counted.
