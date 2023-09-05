![Using commitizen cli](images/demo.gif)

## About

In your terminal run `cz commit` or the shortcut `cz c` to generate a guided git commit.

A commit can be signed off using `cz commit --signoff` or the shortcut `cz commit -s`.

You can run `cz commit --write-message-to-file COMMIT_MSG_FILE` to additionally save the
generated message to a file. This can be combined with the `--dry-run` flag to only
write the message to a file and not modify files and create a commit. A possible use
case for this is to [automatically prepare a commit message](./tutorials/auto_prepare_commit_message.md).

!!! note
    To maintain platform compatibility, the `commit` command disables ANSI escaping in its output.
    In particular, pre-commit hooks coloring will be deactivated as discussed in [commitizen-tools/commitizen#417](https://github.com/commitizen-tools/commitizen/issues/417).

## Configuration

### `always_signoff`

When set to `true`, each commit message created by `cz commit` will be signed off.

Defaults to: `false`.

In your `pyproject.toml` or `.cz.toml`:

```toml
[tool.commitizen]
always_signoff = true
```
