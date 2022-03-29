# Automatically check message before commit

## About
To automatically check a commit message prior to committing, you can use a [git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks).

## How to
There are two common methods for installing the hook:
### Method 1: Add git hook through [pre-commit](https://pre-commit.com/)

* Step 1: Install [pre-commit](https://pre-commit.com/)

```sh
python -m pip install pre-commit
```

* Step 2: Create `.pre-commit-config.yaml` at your root directory with the following content

```yaml
---
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v1.17.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

* Step 3: Install the configuration into git hook through `pre-commit`

```bash
pre-commit install --hook-type commit-msg
```

### Method 2: Manually add git hook
The command might be included inside of a Git hook (inside of `.git/hooks/` at the root of the project).

The selected hook might be the file called commit-msg.

This example shows how to use the check command inside of commit-msg.

At the root of the project:

```bash
cd .git/hooks
touch commit-msg
chmod +x commit-msg
```

Open the file and edit it:

```sh
#!/bin/bash
MSG_FILE=$1
cz check --commit-msg-file $MSG_FILE
```

Where `$1` is the name of the temporary file that contains the current commit message. To be more explicit, the previous variable is stored in another variable called `$MSG_FILE`, for didactic purposes.

The `--commit-msg-file` flag is required, not optional.

Each time you create a commit, automatically, this hook will analyze it.
If the commit message is invalid, it'll be rejected.

The commit should follow the given committing rules; otherwise, it won't be accepted.
