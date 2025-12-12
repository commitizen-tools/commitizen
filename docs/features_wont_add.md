# Feature request graveyard

This page contains features and designs that have been proposed or considered but won't be implemented in Commitizen.

For a comprehensive list, please refer to our [issue tracker](https://github.com/commitizen-tools/commitizen/issues?q=is:issue%20state:closed%20label:%22issue-status:%20wont-fix%22%20OR%20label:%22issue-status:%20wont-implement%22).

## Enable multiple locations of config file `.cz.*` [#955](https://github.com/commitizen-tools/commitizen/issues/955)

<!-- TODO: Add more details about why we won't add this feature -->

## Create a flag to build the changelog from commits in multiple git repositories [#790](https://github.com/commitizen-tools/commitizen/issues/790)

<!-- TODO: Add more details about why we won't add this feature -->

## Global Configuration [#597](https://github.com/commitizen-tools/commitizen/issues/597)

<!-- TODO: Add more details about why we won't add this feature -->

## Why are `revert` and `chore` valid types in the check pattern of `cz_conventional_commits` but not types we can select?

`revert` and `chore` are added to the `pattern` in `cz check` in order to prevent backward errors, but officially they are not part of conventional commits, we are using the latest [types from Angular](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type) (they used to but were removed).
However, you can create a customized `cz` with those extra types. (See [Customization](customization/config_file.md)).

See more discussion in

- [issue #142](https://github.com/commitizen-tools/commitizen/issues/142)
- [issue #36](https://github.com/commitizen-tools/commitizen/issues/36)


## Why not support CalVer?

`commitizen` could support CalVer alongside SemVer, but in practice implementing CalVer
creates numerous edge cases that are difficult to maintain ([#385]) and more generally,
mixing the two version schemes may not be a good idea. If CalVer or other custom
versioning scheme is needed, `commitizen` could still be used to standardize commits
and create changelogs, but a separate package should be used for version increments.

Mixing CalVer and SemVer is generally not recommended because each versioning scheme
serves a different purpose. Diverging from either specification can be confusing to
users and cause errors with third-party tools that don't expect the non-standard format.

In the future, `commitizen` may support some implementation of CalVer, but at the time
of writing, there are no plans to implement the feature ([#173]).

If you would like to learn more about both schemes, there are plenty of good resources:

- [Announcing CalVer](https://sedimental.org/calver.html)
- [API Versioning from Stripe](https://stripe.com/blog/api-versioning)
- [Discussion about pip's use of CalVer](https://github.com/pypa/pip/issues/5645#issuecomment-407192448)
- [Git Version Numbering](https://code.erpenbeck.io/git/2021/12/16/git-version-numbering/)
- [SemVer vs. CalVer and Why I Use Both](https://mikestaszel.com/2021/04/03/semver-vs-calver-and-why-i-use-both/) (but not at the same time)
- [Semver Will Not Save You](https://hynek.me/articles/semver-will-not-save-you/)
- [Why I Don't Like SemVer](https://snarky.ca/why-i-dont-like-semver/)

[#173]: https://github.com/commitizen-tools/commitizen/issues/173
[#385]: https://github.com/commitizen-tools/commitizen/pull/385


## Why don't we use [Pydantic](https://docs.pydantic.dev/)?

While Pydantic is a powerful and popular library for data validation, we intentionally avoid using it in this project to keep our dependency tree minimal and maintainable.

Including Pydantic would increase the chances of version conflicts for users - especially with major changes introduced in Pydantic v3. Because we pin dependencies tightly, adding Pydantic could unintentionally restrict what other tools or libraries users can install alongside `commitizen`.

Moreover we don't rely on the full feature set of Pydantic. Simpler alternatives like Python's built-in `TypedDict` offer sufficient type safety for our use cases, without the runtime overhead or dependency burden.

In short, avoiding Pydantic helps us:

- Keep dependencies lightweight
- Reduce compatibility issues for users
- Maintain clarity about what contributors should and shouldn't use
