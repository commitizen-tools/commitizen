# For AI Agents

These pages are written for AI agents contributing to Commitizen. Human
contributors may also find them useful as a quick reference. They
**complement** the existing human-facing contributor docs rather than
replace them — anything covered by the human docs is linked, not restated.

> If you are an AI agent looking to **use** Commitizen as a tool (validate
> commit messages, bump versions in a downstream project), see the skill
> definition at `.agents/skills/commitizen/SKILL.md` in the repo root.
> The pages here are for working **on** Commitizen itself.

## Source-of-truth map

When two documents could host a piece of guidance, this table is the
tie-breaker. Agent pages that drift from it should be fixed, not the
human pages.

| Topic | Lives in | Why |
|---|---|---|
| Setup, dev workflow, PR lifecycle, labels | [Contributing](../contributing.md) | Same for humans and agents |
| poe command reference | [Contributing TL;DR](../contributing_tldr.md) | One canonical cheat sheet |
| PR etiquette, AI-assisted policy | [Pull Request Guidelines](../pull_request.md) and [PR template](https://github.com/commitizen-tools/commitizen/blob/master/.github/pull_request_template.md) | One canonical policy |
| Codebase topology and extension points | [Architecture Overview](../architecture.md) | Useful to humans too |
| Always-loaded agent rules | [`AGENTS.md`](https://github.com/commitizen-tools/commitizen/blob/master/AGENTS.md) | Auto-loaded as system context every session |
| Targeted test selectors and CI failure recipes | [Validation Guide](validation.md) | Agent-specific |
| Recipes for recurring task types | [Playbooks](#playbooks) | Agent-specific |

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

The repo-root [`AGENTS.md`](https://github.com/commitizen-tools/commitizen/blob/master/AGENTS.md)
is the auto-loaded entry point for most agent tools. It holds the rules an
agent needs in every session; this page is the deeper reference.

## Agent-specific deltas

Humans absorb these rules through review; agents need them stated:

1. **Complete the PR template fully**, including the AI-disclosure checkbox
   and the `Generated-by:` trailer. The maintainers re-run the commands you
   list under "Steps to Test This Pull Request" — make them exact.
2. **`uv run poe all` is the pre-push verification command** named in the
   PR template. `poe ci` is the CI-equivalent runner (uses `prek` and does
   not auto-format); run it too if you want to mirror CI exactly. See the
   [Validation Guide](validation.md#choosing-a-final-check) for the
   distinction.
3. **Do not touch generated artifacts.** See the do-not-touch list in
   [`AGENTS.md`](https://github.com/commitizen-tools/commitizen/blob/master/AGENTS.md).
4. **Prefer targeted test selectors during iteration** — see the
   [targeted-test map](validation.md#targeted-test-map). The full suite
   is fine for a final pre-push run.

## Playbooks

Recipes for recurring task types. Each playbook is self-contained: trigger,
files to read first, ordered steps, verification commands, and known
pitfalls. They link out to the human-facing concept docs rather than
restating concepts.

- [Add a version provider](playbooks/add-version-provider.md)
- [Add a changelog format](playbooks/add-changelog-format.md)
- [Add or modify a CLI flag](playbooks/add-cli-flag.md)
- [Deprecate a public API](playbooks/deprecate-public-api.md)
- [Update generated snapshots and screenshots](playbooks/update-snapshots.md)

If your task does not match a playbook, fall back to the general flow:

1. Read the [Architecture Overview](../architecture.md) for the relevant
   subsystem.
2. Read 1–2 existing examples in the same directory to match local
   conventions.
3. Make the change, plus tests, plus user-facing docs.
4. Iterate with targeted tests; finish with `uv run poe all`.
5. Open the PR using the template; check the AI-disclosure box.

## Updating these pages

Treat these pages like any other code change: open a PR, follow the
template, run `uv run poe doc:build` to verify the mkdocs build, and
check internal links for breakage. If you find yourself restating
something that already lives in a human-facing doc, link to it instead
and shorten the agent doc.
