# Automatically prepare message before commit

## About

To automatically prepare a commit message prior to committing, you can use a [Git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks).

## How to

- Step 1: Create a new [`prepare-commit-msg`][prepare-commit-msg-docs] Git hook by running the following commands from the root of the Git repository:

```sh
cd .git/hooks
touch prepare-commit-msg
chmod +x prepare-commit-msg
```

- Step 2: Edit the newly created file and add the following content:

```sh
#!/bin/sh
COMMIT_MSG_FILE=$1
exec < /dev/tty && cz commit --dry-run --write-message-to-file $COMMIT_MSG_FILE || true
```

See the Git hooks documentation on [`prepare-commit-msg` hooks][prepare-commit-msg-docs] for details on how this works.

[prepare-commit-msg-docs]: https://git-scm.com/docs/githooks#_prepare_commit_msg
