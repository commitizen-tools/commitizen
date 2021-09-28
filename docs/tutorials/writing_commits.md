For this project to work well in your pipeline, a commit convention must be followed.

By default commitizen uses the known [conventional commits][conventional_commits], but
you can create your own following the docs information over at
[customization][customization].

## Conventional commits

If you are using [conventional commits][conventional_commits], the most important
thing to know is that you must begin your commits with at least one of these tags:
`fix`, `feat`. And if you introduce a breaking change, then, you must
add to your commit body the following `BREAKING CHANGE`.
Using these 3 keywords will allow the proper identification of the semantic version.
Of course, there are other keywords, but I'll leave it to the reader to explore them.

## Writing commits

Now to the important part, when writing commits, it's important to think about:

- Your future self
- Your colleagues

You may think this is trivial, but it's not. It's important for the reader to
understand what happened.

### Recommendations

- **Keep the message short**: Makes the list of commits more readable (~50 chars).
- **Talk imperative**: Follow this rule: `If applied, this commit will <commit message>`
- **Think about the CHANGELOG**: Your commits will probably end up in the changelog
  so try writing for it, but also keep in mind that you can skip sending commits to the
  CHANGELOG by using different keywords (like `build`).
- **Use a commit per new feature**: if you introduce multiple things related to the same
  commit, squash them. This is useful for auto-generating CHANGELOG.

| Do's | Don'ts |
| ---- | ------ |
| `fix(commands): bump error when no user provided` | `fix: stuff` |
| `feat: add new commit command` | `feat: commit command introduced` |

[customization]: customization.md
[conventional_commits]: https://www.conventionalcommits.org
