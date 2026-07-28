# For AI Agents

These pages are written for AI agents contributing to Commitizen. Human contributors may also find them useful as a quick reference. They **complement** the existing human-facing contributor docs rather than replace them — anything covered by the human docs is linked, not restated.

> If you are an AI agent looking to **use** Commitizen as a tool (validate
> commit messages, bump versions in a downstream project), see the skill
> definition at `.agents/skills/commitizen/SKILL.md` in the repo root.
> The pages here are for working **on** Commitizen itself.

## When to read what

| You want to... | Read |
|---|---|
| Set up a local dev environment | [Contributing](../contributing.md#prerequisites-setup) |
| Look up a poe command | [Contributing TL;DR](../contributing_tldr.md#command-cheat-sheet) |
| Understand the codebase layout and extension points | [Architecture Overview](../architecture.md) |
| Open a pull request | [Pull Request Guidelines](../pull_request.md) and the [PR template](https://github.com/commitizen-tools/commitizen/blob/master/.github/pull_request_template.md) |
| Pick the right test selector for a change | [Validation Guide](validation.md#targeted-test-map) |
| Recover from a CI failure | [Validation Guide](validation.md#ci-failure-recipes) |
| Implement a recurring task type | [Playbooks](#playbooks) |

The repo-root [`AGENTS.md`](https://github.com/commitizen-tools/commitizen/blob/master/AGENTS.md) is the auto-loaded entry point for most agent tools. It holds the rules an agent needs in every session; this page is the deeper reference.

## Playbooks

Recipes for recurring task types. Each playbook is self-contained: trigger, files to read first, ordered steps, verification commands, and known pitfalls. They link out to the human-facing concept docs rather than restating concepts.

- [Add a version provider](playbooks/add-version-provider.md)
- [Add a changelog format](playbooks/add-changelog-format.md)
- [Add or modify a CLI flag](playbooks/add-cli-flag.md)
- [Deprecate a public API](playbooks/deprecate-public-api.md)
- [Update generated snapshots and screenshots](playbooks/update-snapshots.md)

If no playbook matches, read the [Architecture Overview](../architecture.md) for the relevant subsystem and follow 1-2 existing examples in the same directory before changing code.

## Updating these pages

Treat these pages like any other code change: open a PR, follow the template, run `uv run poe doc:build` to verify the mkdocs build, and check internal links. If you find yourself restating something that already lives in a human-facing doc, link to it instead and shorten the agent doc.
