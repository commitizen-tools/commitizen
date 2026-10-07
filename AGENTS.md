# AGENT

- When writing something intended for human consumption (comment, commit message, reply to prompt, documentation, etc.), keep answers short and concise
- Technical prose only, be direct. Use ASD-STE100 (Simplified Technical English)
- Use concise, clear, simple language. Define unavoidable jargon before using it
- Code explains the how. You must always document the code's what and why
- Always disclose if it was made by an AI model (commit footer, pull request body) with `Assisted By: AI`
- Ask for clarification if in doubt, don't assume. And if the user provides insightful context, add it to the documentation
- Always write and maintain the documentation under `docs/`, if it doesn't exist create it, use the context and intuition gathered while coding and interacting with the user.
- Don't touch blocks of code unrelated to the feature you implement. E.g. Don't add comments to a block of code if you did not create it or modify it
- Follow the Liskov substitution principle: design by contract
- Pull requests must follow the [guidelines](docs/contributing/pull_request.md) and the template in `.github/pull_request_template.md`.
- Commit messages must follow [docs/tutorials/writing_commits.md](docs/tutorials/writing_commits.md).

## Purpose

`commitizen` is a tool for release management, with automatic version bump (git tag and file updates), changelog generation, and commit message enforcement (defaults to "conventional commits").

## Coding

Review [`docs/contributing/contributing.md`](docs/contributing/contributing.md)

Main commands

```
uv run poe format
uv run poe lint
uv run poe test
uv run poe ci  # commit check + pre-commit hooks via `prek` + test with coverage
uv run poe all  # format + lint + check-commit + coverage
```

## Python

- Write the Python code with strict type hinting
- Prefer `enum.StrEnum` to represent states
- Preserve public behavior and CLI UX (`commitizen/cli.py`), no breaking changes to APIs, CLI flags, or exit codes unless explicitly requested.
- Errors: Prefer `commitizen/exceptions.py` error types; keep messages clear for CLI users.

### Testing

You MUST exclusively use `pytest`.
You MUST adhere to the following standards:

- Structure: Follow the Arrange, Act, Assert (AAA) pattern. Visually separate these phases with blank lines and comments
- Fixtures over Inline Setup: Use existing `pytest` fixtures to create git projects, files, tags, etc. Do not pollute the test body with complex setup logic if it can be abstracted into a fixture
- Test Documentation: Complex tests must include a brief docstring explaining the business scenario or edge case being validated, or issue worked on.

## Documentation Guidelines

- ALWAYS document functions and classes
- Use Google Docstring Style with these major modifications:
  - NEVER include type hints in the docstring. We rely exclusively on Python's PEP 484 type signatures
  - Classes MUST include an example. Any class documentation must contain a brief usage example formatted in markdown
  - Class Attributes MUST be documented. The class docstring must document the instance variables initialized in `__init__` within an `Attributes:` section
- If the code is too complex or solutions are discarded, document them in a **Notes** section
- Even simple functions or internal helpers require documentation to explain their context
