# Automatically prepare message before commit

## About

It can be desirable to use Commitizen for all types of commits (i.e. regular, merge,
squash) so that the complete git history adheres to the commit message convention
without ever having to call `cz commit`.

To automatically prepare a commit message prior to committing, you can
use a [prepare-commit-msg Git hook][prepare-commit-msg-docs]:

> This hook is invoked by git-commit right after preparing the
> default log message, and before the editor is started.

To automatically perform arbitrary cleanup steps after a successful commit you can use a
[post-commit Git hook][post-commit-docs]:

> This hook is invoked by git-commit. It takes no parameters, and is invoked after a
> commit is made.

A combination of these two hooks allows for enforcing the usage of Commitizen so that
whenever a commit is about to be created, Commitizen is used for creating the commit
message. Running `git commit` or `git commit -m "..."` for example, would trigger
Commitizen and use the generated commit message for the commit.

## Installation

Copy the hooks from [here](https://github.com/commitizen-tools/commitizen/tree/master/hooks) into the `.git/hooks` folder and make them
  executable by running the following commands from the root of your Git repository:

```bash
wget -O .git/hooks/prepare-commit-msg https://raw.githubusercontent.com/commitizen-tools/commitizen/master/hooks/prepare-commit-msg.py
chmod +x .git/hooks/prepare-commit-msg
wget -O .git/hooks/post-commit https://raw.githubusercontent.com/commitizen-tools/commitizen/master/hooks/post-commit.py
chmod +x .git/hooks/post-commit
```

## Features

- Commits can be created using both `cz commit` and the regular `git commit`
- The hooks automatically create a backup of the commit message that can be reused if
  the commit failed
- The commit message backup can also be used via `cz commit --retry`

[post-commit-docs]: https://git-scm.com/docs/githooks#_post_commit
[prepare-commit-msg-docs]: https://git-scm.com/docs/githooks#_prepare_commit_msg
