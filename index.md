______________________________________________________________________

[**Commitizen Documentation Site**](https://commitizen-tools.github.io/commitizen/)

______________________________________________________________________

## About

Commitizen is a powerful release management tool that helps teams maintain consistent and meaningful commit messages while automating version management.

### What Commitizen Does

By enforcing standardized commit conventions (defaulting to [Conventional Commits](https://www.conventionalcommits.org)), Commitizen helps teams:

- Write clear, structured commit messages
- Automatically manage version numbers using semantic versioning
- Generate and maintain changelogs
- Streamline the release process

### Key Benefits

With just a simple `cz bump` command, Commitizen handles:

1. **Version Management**: Automatically bumps version numbers and updates version files based on your commit history
1. **Changelog Generation**: Creates and updates changelogs following the [Keep a changelog](https://keepachangelog.com/) format
1. **Commit Standardization**: Enforces consistent commit message formats across your team

This standardization makes your commit history more readable and meaningful, while the automation reduces manual work and potential errors in the release process.

### Features

- Interactive CLI for standardized commits with default [Conventional Commits](https://www.conventionalcommits.org) support
- Intelligent [version bumping](https://commitizen-tools.github.io/commitizen/commands/bump/) using [Semantic Versioning](https://semver.org/)
- Automatic [keep a changelog](https://keepachangelog.com/) generation
- Built-in commit validation with pre-commit hooks
- [Customizable](https://commitizen-tools.github.io/commitizen/customization/config_file/) commit rules and templates
- Multi-format version file support
- Custom rules and plugins via pip

## Getting Started

### Requirements

Before installing Commitizen, ensure you have:

- [Python](https://www.python.org/downloads/) `3.10+`
- [Git](https://git-scm.com/downloads) `1.8.5.2+`

### Installation

#### Global Installation (Recommended)

The recommended way to install Commitizen is using [`pipx`](https://pipx.pypa.io/) or [`uv`](https://docs.astral.sh/uv/), which ensures a clean, isolated installation:

**Using pipx:**

```
# Install Commitizen
pipx install commitizen

# Keep it updated
pipx upgrade commitizen
```

**Using uv:**

```
# Install commitizen
uv tool install commitizen

# Keep it updated
uv tool upgrade commitizen
```

**(For macOS users) Using Homebrew:**

```
brew install commitizen
```

#### Project-Specific Installation

You can add Commitizen to your Python project using any of these package managers:

**Using pip:**

```
pip install -U commitizen
```

**Using conda:**

```
conda install -c conda-forge commitizen
```

**Using Poetry:**

```
# For Poetry >= 1.2.0
poetry add commitizen --group dev

# For Poetry < 1.2.0
poetry add commitizen --dev
```

**Using uv:**

```
uv add --dev commitizen
```

**Using pdm:**

```
pdm add -d commitizen
```

### Basic Commands

#### Initialize Commitizen

To get started, run the `cz init` command. This will guide you through the process of creating a configuration file with your preferred settings.

#### Create Commits

Create standardized commits using:

```
cz commit
# or use the shortcut
cz c
```

To sign off your commits:

```
cz commit -- --signoff
# or use the shortcut
cz commit -- -s
```

For more commit options, run `cz commit --help`.

#### Version Management

The most common command you'll use is:

```
cz bump
```

This command:

- Bumps your project's version
- Creates a git tag
- Updates the changelog (if `update_changelog_on_bump` is enabled)
- Updates version files

You can customize:

- [Version files](https://commitizen-tools.github.io/commitizen/commands/bump/#version_files)
- [Version scheme](https://commitizen-tools.github.io/commitizen/commands/bump/#version_scheme)
- [Version provider](https://commitizen-tools.github.io/commitizen/config/version_provider/)

For all available options, see the [bump command documentation](https://commitizen-tools.github.io/commitizen/commands/bump/).

### Advanced Usage

#### Get Project Version

```
# Get your project's version (instead of Commitizen's version)
cz version -p
# Preview changelog changes
cz changelog --dry-run "$(cz version -p)"
```

This command is particularly useful for automation scripts and CI/CD pipelines.

For example, you can use the output of the command `cz changelog --dry-run "$(cz version -p)"` to notify your team about a new release in Slack.

#### Prek and Pre-commit Integration

Commitizen can automatically validate your commit messages using pre-commit hooks.

1. Add to your `.pre-commit-config.yaml`:

   ```
   ---
   repos:
     - repo: https://github.com/commitizen-tools/commitizen
       rev: master  # Replace with latest tag
       hooks:
         - id: commitizen
         - id: commitizen-branch
           stages: [pre-push]
   ```

1. Install the hooks:

   ```
   prek install --hook-type commit-msg --hook-type pre-push
   ```

| Hook              | Recommended Stage |
| ----------------- | ----------------- |
| commitizen        | commit-msg        |
| commitizen-branch | pre-push          |

> **Note**: Replace `master` with the [latest tag](https://github.com/commitizen-tools/commitizen/tags) to avoid warnings. You can automatically update this with:
>
> ```
> prek autoupdate
> ```

For more details about commit validation, see the [check command documentation](https://commitizen-tools.github.io/commitizen/commands/check/).

## Help & Reference

### Command Line Interface

Commitizen provides a comprehensive CLI with various commands. Here's the complete reference:

### Quick Reference

| Command        | Description                         | Alias   |
| -------------- | ----------------------------------- | ------- |
| `cz init`      | Initialize Commitizen configuration | -       |
| `cz commit`    | Create a new commit                 | `cz c`  |
| `cz bump`      | Bump version and update changelog   | -       |
| `cz changelog` | Generate changelog                  | `cz ch` |
| `cz check`     | Validate commit messages            | -       |
| `cz version`   | Show version information            | -       |

### Additional Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org)
- [Exit Codes Reference](https://commitizen-tools.github.io/commitizen/exit_codes/)
- [Configuration Guide](https://commitizen-tools.github.io/commitizen/config/configuration_file/)
- [Command Documentation](https://commitizen-tools.github.io/commitizen/commands/init/)

### Getting Help

For each command, you can get detailed help by adding `--help`:

```
cz commit --help
cz bump --help
cz changelog --help
```

For more details, visit our [documentation site](https://commitizen-tools.github.io/commitizen/).

## Setting up bash completion

Commitizen supports command-line completion through [argcomplete](https://kislyuk.github.io/argcomplete/), which is automatically installed as a dependency. This feature provides intelligent auto-completion for all Commitizen commands and options.

### Supported Shells

- **Bash**: Full support
- **Zsh**: Limited support
- **Fish**: Limited support
- **Tcsh**: Limited support

### Installation Methods

#### Global Installation (Recommended)

If you installed Commitizen globally (e.g., using `pipx` or `brew`), you can enable global completion:

```
# Enable global completion for all Python applications
sudo activate-global-python-argcomplete
```

#### User-Specific Installation

For a user-specific installation that persists across sessions:

```
# Add to your shell's startup file (e.g., ~/.bashrc, ~/.zshrc)
register-python-argcomplete cz >> ~/.bashrc
```

#### Temporary Installation

For one-time activation in your current shell session:

```
# Activate completion for current session only
eval "$(register-python-argcomplete cz)"
```

### Verification

After installation, you can verify the completion is working by:

1. Opening a new terminal session
1. Typing `cz` followed by a space and pressing `TAB` twice
1. You should see a list of available commands

For more detailed information about argcomplete configuration and troubleshooting, visit the [argcomplete documentation](https://kislyuk.github.io/argcomplete/).

## Star History

## Sponsors

These are our cool sponsors!
