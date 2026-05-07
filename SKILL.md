---
name: commitizen
description: Use this skill for tasks involving Conventional Commits, commit message validation, Commitizen configuration, semantic version bumps, changelog generation, or CI/release automation with the Commitizen CLI.
license: MIT
compatibility: Git repository with Python and Commitizen available as `cz` or runnable from source. Network access is optional and mainly relevant for CI or release integrations.
metadata:
  project: commitizen-tools/commitizen
  docs: https://commitizen-tools.github.io/commitizen/
  install: pip install commitizen | uv add commitizen
---

# Commitizen

Commitizen is a CLI for enforcing Conventional Commits, automating version bumps, and generating changelogs.

## Use this skill when

- A task involves commit message authoring or validation.
- A repository needs Commitizen initialization or configuration updates.
- Work depends on version schemes, version providers, version files, tags, or changelog behavior.
- CI/CD automation needs commit validation, automated version bumps, or release notes.

## Core workflow

1. Find the active configuration file in this order: `.cz.toml`, `cz.toml`, `.cz.json`, `cz.json`, `.cz.yaml`, `cz.yaml`, then `pyproject.toml` under `[tool.commitizen]`.
2. Read the effective settings before acting, especially `name`, `version`, `version_provider`, `version_scheme`, `version_files`, `tag_format`, `update_changelog_on_bump`, `annotated_tag`, `bump_message`, `pre_bump_hooks`, and `post_bump_hooks`.
3. Match the command to the task:
   - `cz commit` for interactive commit authoring
   - `cz check` for validating commit messages or git ranges
   - `cz init` for bootstrapping configuration
   - `cz bump` for calculating or applying release versions
   - `cz changelog` for generating or updating `CHANGELOG.md`
   - `cz ls` for listing available commit rules
   - `cz version` for showing the current version
4. Prefer read-only inspection first. Safe discovery commands include `cz version`, `cz ls`, `cz check`, `cz bump --get-next`, and `cz bump --dry-run`.
5. Treat `cz bump` as stateful: it can update version files, create a bump commit, and create a git tag. Verify the version provider, version scheme, tag format, and changelog settings before running it for real.
6. When automating in CI, check whether the workflow should ignore specific exit codes with `--no-raise` and whether `bump_message` should include skip-CI text.
7. After making changes, validate the resulting configuration, commands, and automation against the repository's actual version scheme and provider.

## Important domain details

- Commitizen installs with `pip install commitizen` or `uv add commitizen`.
- The default version scheme is PEP 440; `semver` and `semver2` are also supported.
- Common version providers include `commitizen`, `pep621`, `poetry`, `cargo`, `npm`, `composer`, `uv`, and `scm`.
- `cz changelog` generates Markdown changelogs.
- `cz commit` supports `--dry-run` and `--write-message-to-file`.
- `cz check` can validate a literal message, a commit-msg file, or a git revision range.

## Suggested references

- Command docs:
  - `docs/commands/commit.md`
  - `docs/commands/bump.md`
  - `docs/commands/changelog.md`
  - `docs/commands/check.md`
  - `docs/commands/init.md`
- Config docs:
  - `docs/config/configuration_file.md`
  - `docs/config/option.md`
  - `docs/config/bump.md`
- Automation docs:
  - `docs/tutorials/github_actions.md`
  - `docs/tutorials/gitlab_ci.md`
- Error handling:
  - `docs/exit_codes.md`

## Examples

- Validate one message: `cz check --message "feat(cli): add release command"`
- Validate branch history: `cz check --rev-range master..HEAD`
- Preview the next version: `cz bump --get-next`
- Preview bump details: `cz bump --dry-run`
- Preview changelog output: `cz changelog --dry-run`
- Initialize configuration: `cz init`
