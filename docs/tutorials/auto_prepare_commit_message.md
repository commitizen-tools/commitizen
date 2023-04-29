# Automatically prepare message before commit

## About

It can be desirable to use commitizen for all types of commits (i.e. regular, merge,
squash) so that the complete git history adheres to the commit message convention
without ever having to call `cz commit` manually.

To automatically prepare a commit message prior to committing, you can
use a [Git hook](prepare-commit-msg-docs):

> The [prepare-commit-msg] hook is invoked by git-commit right after preparing the
> default log message, and before the editor is started.

This allows for enforcing the usage of commitizen so that whenever a commit is about to
be created, commitizen is used for creating the commit message. Running `git commit` or
`git commit -m "..."` for example, would trigger commitizen and use the generated commit
message for the commit.

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

## Drawbacks

If additional hooks are used (e.g. pre-commit) that prevent a commit from being created,
the message has to be created from scratch when commiting again.
