# Commit Message Best Practices

## About

For Commitizen to work effectively in your development pipeline, commits must follow a consistent convention. By default, Commitizen uses the [Conventional Commits][conventional_commits] specification, which provides a standardized format for commit messages that enables automatic versioning and changelog generation.

You can also create your own custom commit convention by following the [customization documentation][customization].

## Conventional Commits Format

The Conventional Commits specification follows this structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Commit Types

Commit types categorize the nature of your changes. The most important types for semantic versioning are:

- **`feat`**: Introduces a new feature (correlates with **MINOR** version increment)
- **`fix`**: Patches a bug (correlates with **PATCH** version increment)

Other commonly used types include:

- **`docs`**: Documentation only changes
- **`style`**: Code style changes (formatting, missing semicolons, etc.)
- **`refactor`**: Code refactoring without changing functionality
- **`perf`**: Performance improvements
- **`test`**: Adding or updating tests
- **`build`**: Changes to build system or dependencies
- **`ci`**: Changes to CI configuration files
- **`chore`**: Other changes that don't modify source or test files

!!! note
    While `feat` and `fix` directly affect semantic versioning, other types (like `build`, `chore`, `docs`) typically don't trigger version bumps unless they include a `BREAKING CHANGE`.

### Breaking Changes

Breaking changes trigger a **MAJOR** version increment. You can indicate breaking changes in two ways:

1. **In the commit body or footer**:
    ```
    feat(api): change authentication method

    BREAKING CHANGE: The authentication API now requires OAuth2 instead of API keys.
    ```

2. **In the commit title** (when enabled):
    ```
    feat!: change authentication method
    ```

    To enable this syntax, set `breaking_change_exclamation_in_title = true` in your configuration. [Read more][breaking-change-config]

### Scope

An optional scope can be added to provide additional context about the area of the codebase affected:

```
feat(parser): add support for JSON arrays
fix(api): handle null response gracefully
```

## Writing Effective Commit Messages

Well-written commit messages are crucial for maintaining a clear project history. When writing commits, consider:

- **Your future self**: You'll need to understand these changes months later
- **Your team**: Clear messages help colleagues understand the codebase evolution
- **Automated tools**: Good messages enable better changelog generation and versioning

### Best Practices

#### 1. Keep the Subject Line Concise

The subject line should be clear and concise (aim for ~50 characters). It should summarize what the commit does in one line.

**Good:**
```
fix(commands): handle missing user input gracefully
feat(api): add pagination support
```

**Avoid:**
```
fix: stuff
feat: commit command introduced
```

#### 2. Use Imperative Mood

Write commit messages in the imperative mood, as if completing the sentence: "If applied, this commit will..."

**Good:**
```
feat: add user authentication
fix: resolve memory leak in parser
```

**Avoid:**
```
feat: added user authentication
fix: resolved memory leak in parser
```

#### 3. Think About the Changelog

Your commits will likely appear in the automatically generated changelog. Write messages that make sense in that context. If you want to exclude a commit from the changelog, use types like `build`, `chore`, or `ci`.

#### 4. One Feature Per Commit

Keep commits focused on a single change. If you introduce multiple related changes, consider squashing them into a single commit. This makes the history cleaner and improves changelog generation.

#### 5. Use the Body for Context

For complex changes, use the commit body to explain:

- **Why** the change was made
- **What** was changed (if not obvious from the subject)
- **How** it differs from previous behavior

```
feat(api): add rate limiting

Implement rate limiting to prevent API abuse. The system now
enforces a maximum of 100 requests per minute per IP address.
Exceeding this limit returns a 429 status code.
```

### Examples

| ✅ Good Examples | ❌ Poor Examples |
| ---------------- | ---------------- |
| `fix(commands): bump error when no user provided` | `fix: stuff` |
| `feat(api): add pagination to user list endpoint` | `feat: commit command introduced` |
| `docs: update installation instructions` | `docs: changes` |
| `refactor(parser): simplify token extraction logic` | `refactor: code cleanup` |

## Character Encoding

Commitizen supports Unicode characters (including emojis) in commit messages. This is useful if you're using commit message formats that include emojis, such as [cz-emoji][cz_emoji].

By default, Commitizen uses `utf-8` encoding. You can configure a different encoding through the `encoding` [configuration option][configuration].

## Related Documentation

- [Conventional Commits Specification][conventional_commits]
- [Custom Commit Conventions][customization]
- [Commit Configuration Options](../config/commit.md)

[customization]: ../customization/config_file.md
[conventional_commits]: https://www.conventionalcommits.org
[cz_emoji]: ../third-party-plugins/cz-emoji.md
[configuration]: ../config/commit.md#encoding
[breaking-change-config]: ../config/commit.md#breaking_change_exclamation_in_title
