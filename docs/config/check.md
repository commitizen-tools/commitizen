# Check Options

<!-- When adding a new option, please keep the alphabetical order. -->

## `allow_abort`

- Type: `bool`
- Default: `False`

Disallow empty commit messages. Useful in CI.

## `allowed_prefixes`

- Type: `list`
- Default: `["Merge", "Revert", "Pull request", "fixup!", "squash!"]`

List of prefixes that commitizen ignores when verifying messages.

## `message_length_limit`

- Type: `int`
- Default: `0` (no limit)

Maximum length of the commit message. Setting it to `0` disables the length limit.

!!! note
    This option can be overridden by the `-l/--message-length-limit` command line argument.
