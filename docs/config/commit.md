# Commit Options

<!-- When adding a new option, please keep the alphabetical order. -->

## `breaking_change_exclamation_in_title`

- Type: `bool`
- Default: `False`

When true, breaking changes will be also indicated by an exclamation mark in the commit title (e.g., `feat!: breaking change`).

When false, breaking changes will be only indicated by `BREAKING CHANGE:` in the footer. See [writing commits](../tutorials/writing_commits.md) for more details.

## `commit_encoding`

- Type: `str`
- Default: `None`

Sets the character encoding of the files that hold a commit message:

- the file that `cz commit --edit` opens in the editor
- the file that `cz commit --write-message-to-file` writes
- the backup file that `cz commit --retry` reads
- the file that `cz check --commit-msg-file` reads

If it is not set, Commitizen uses [`encoding`](#encoding). Set it when your editor saves commit messages in a different encoding from your other files.

## `encoding`

- Type: `str`
- Default: `"utf-8"`

Sets the character encoding to be used when parsing commit messages.

## `retry_after_failure`

- Type: `bool`
- Default: `False`

Retries failed commit when running `cz commit`.
