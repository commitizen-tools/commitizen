![Using commitizen cli](images/demo.gif)

## About

In your terminal run `cz commit` or the shortcut `cz c` to generate a guided git commit.

A commit can be signed off using `cz commit --signoff` or the shortcut `cz commit -s`.

You can run `cz commit --write-message-to-file COMMIT_MSG_FILE` to additionally save the
generated message to a file. This can be combined with the `--dry-run` flag to only
write the message to a file and not modify files and create a commit.

!!! note
    To maintain platform compatibility, the `commit` command disable ANSI escaping in its output.
    In particular pre-commit hooks coloring will be deactivated as discussed in [commitizen-tools/commitizen#417](https://github.com/commitizen-tools/commitizen/issues/417).
