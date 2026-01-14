# Automatically check message before commit

## About

To automatically check a commit message prior to committing, you can use a [Git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks). This ensures that all commit messages follow your project's commitizen format before they are accepted into the repository.

When a commit message fails validation, Git will reject the commit and display an error message explaining what went wrong. You'll need to amend your commit message to follow the required format before the commit can proceed.

## How to

There are two common methods for installing the hooks:

### Method 1: Using [pre-commit](https://pre-commit.com/) (Recommended)

[pre-commit](https://pre-commit.com/) is a framework for managing and maintaining multi-language pre-commit hooks. It's the recommended approach as it handles hook installation, updates, and execution automatically.

#### Step 1: Install pre-commit

```sh
python -m pip install pre-commit
```

#### Step 2: Create `.pre-commit-config.yaml`

Create a `.pre-commit-config.yaml` file in your project root directory with the following content:

```yaml
---
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v4.10.0  # Use the latest version or a specific version
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

!!! tip "Using the latest version"
    Replace `v4.10.0` with the latest commitizen version. You can find the latest version on [GitHub releases](https://github.com/commitizen-tools/commitizen/releases) or use a specific commit SHA for pinning to an exact version.

#### Step 3: Install the hook

Install the configuration into Git's hook system:

```bash
pre-commit install --hook-type commit-msg
```

The hook is now active! Every time you create a commit, commitizen will automatically validate your commit message.

### Method 2: Manual Git hook installation

If you prefer not to use pre-commit, you can manually create a Git hook. This gives you full control over the hook script but requires manual maintenance.

#### Step 1: Create the commit-msg hook

Navigate to your project's `.git/hooks` directory and create the `commit-msg` hook file:

```bash
cd .git/hooks
touch commit-msg
chmod +x commit-msg
```

#### Step 2: Add the commitizen check command

Open the `commit-msg` file in your editor and add the following content:

```bash
#!/bin/bash
cz check --allow-abort --commit-msg-file $1
```

Where:

- `$1` is the temporary file path that Git provides, containing the current commit message
- `--allow-abort` allows empty commit messages (which typically instruct Git to abort a commit)
- `--commit-msg-file` tells commitizen to read the commit message from the specified file

The hook is now active! Each time you create a commit, this hook will automatically validate your commit message.

## Testing the hook

After installing the hook, you can test it by attempting to commit with an invalid message:

```bash
# This should fail with an invalid message
git commit -m "invalid commit message"

# This should succeed with a valid message
git commit -m "feat: add new feature"
```

If the hook is working correctly, invalid commit messages will be rejected with an error message explaining what's wrong.

## What happens when validation fails?

When a commit message fails validation:

1. Git will abort the commit
2. An error message will be displayed showing:
   - Which commit failed (if checking multiple commits)
   - The invalid commit message
   - The expected pattern/format
3. Your changes remain staged, so you can simply amend the commit message and try again

Example error output:

<!-- DEPENDENCY: InvalidCommitMessageError -->

```
commit validation: failed!
please enter a commit message in the commitizen format.
commit "abc123": "invalid message"
pattern: ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .{1,}
```

## Troubleshooting

### Hook not running

- **Verify the hook file exists**: Check that `.git/hooks/commit-msg` exists and is executable
- **Check file permissions**: Ensure the hook has execute permissions (`chmod +x .git/hooks/commit-msg`)
- **Verify commitizen is installed**: Run `cz --version` to confirm commitizen is available in your PATH
- **Check Git version**: Ensure you're using a recent version of Git that supports hooks

### Pre-commit hook not working

- **Verify installation**: Run `pre-commit --version` to confirm pre-commit is installed
- **Reinstall the hook**: Try running `pre-commit install --hook-type commit-msg` again
- **Check configuration**: Verify your `.pre-commit-config.yaml` file is valid YAML and in the project root
- **Update hooks**: Run `pre-commit autoupdate` to update to the latest versions

### Bypassing the hook (when needed)

If you need to bypass the hook temporarily (e.g., for merge commits or special cases), you can use:

```bash
git commit --no-verify -m "your message"
```

!!! warning "Use with caution"
    Only bypass hooks when absolutely necessary, as it defeats the purpose of automated validation.

## Additional resources

- Learn more about [Git hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- See the [check command documentation](../commands/check.md) for more validation options
- Check out [pre-commit documentation](https://pre-commit.com/) for advanced hook management
