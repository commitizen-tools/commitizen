## About

This feature enforces the project to always use conventional-commits by doing this in a pre-commit hook.

The command might be included inside of a Git hook (inside of `.git/hooks/` at the root of the project).

The selected hook might be the file called commit-msg.

This an example showing how to use the check command inside of commit-msg.

At the root of the project:

```sh
$ cd .git/hooks
$ touch commit-msg
$ chmod +x commit-msg
```

Open the file and edit it:

```sh
#!/bin/bash
MSG_FILE=$1
cz check --commit-msg-file $MSG_FILE
```

Where $1 is the name of the temporary file that contains the current commit message. To be more explicit, the previous variable is stored in another variable called $MSG_FILE, for didactic purposes.

The --commit-msg-file flag is required, not optional.

Each time you create a commit, automatically, this hook will analyze it.
If the commit message is invalid, it'll be rejected.

The commit should follows the conventional commit convention, otherwise it won't be accepted.
