## Contributing to commitizen

First of all, thank you for taking the time to contribute! 🎉

When contributing to [commitizen](https://github.com/commitizen-tools/commitizen), please first create an [issue](https://github.com/commitizen-tools/commitizen/issues) to discuss the change you wish to make before making a change.

If you're a first-time contributor, you can check the issues with [good first issue](https://github.com/commitizen-tools/commitizen/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) tag.

## Install before contributing

1. Install [poetry](https://python-poetry.org/) `>=2.0.0`. See installation [pages](https://python-poetry.org/docs/#installing-with-the-official-installer).
2. Install [gpg](https://gnupg.org). See installation [pages](https://gnupg.org/documentation/manuals/gnupg/Installation.html#Installation). For Mac users, you can use [homebrew](https://brew.sh/).

## Before making a pull request

1. Fork [the repository](https://github.com/commitizen-tools/commitizen).
1. Clone the repository from your GitHub.
1. Set up development environment through [poetry](https://python-poetry.org/) (`poetry install`).
1. Set up [pre-commit](https://pre-commit.com/) hook (`poetry setup-pre-commit`).
1. Checkout a new branch and add your modifications.
1. Add test cases for all your changes.
   (We use [CodeCov](https://codecov.io/) to ensure our test coverage does not drop.)
1. Use [commitizen](https://github.com/commitizen-tools/commitizen) to do git commit. We follow [conventional commits](https://www.conventionalcommits.org/).
1. Run `poetry all` to ensure you follow the coding style and the tests pass.
1. Optionally, update the `./docs/README.md` or `docs/images/cli_help` (through running `poetry doc:screenshots`).
1. **Do not** update the `CHANGELOG.md`; it will be automatically created after merging to `master`.
1. **Do not** update the versions in the project; they will be automatically updated.
1. If your changes are about documentation, run `poetry doc` to serve documentation locally and check whether there are any warnings or errors.
1. Send a [pull request](https://github.com/commitizen-tools/commitizen/pulls) 🙏

## Use of GitHub Labels

* good-first-issue *(issue only)*
* help-wanted
* issue-status: needs-triage *(issue only)* **(default label for issues)**
* issue-status: wont-fix
* issue-status: wont-implement
* issue-status: duplicate
* issue-status: invalid
* issue-status: wait-for-response
* issue-status: wait-for-implementation
* issue-status: pr-created
* pr-status: wait-for-review **(default label for PRs)**
* pr-status: reviewing
* pr-status: wait-for-modification
* pr-status: wait-for-response
* pr-status: ready-to-merge
* needs: test-case *(PR only)*
* needs: documentation *(PR only)*
* type: feature
* type: bug
* type: documentation
* type: refactor
* type: question *(issue only)*
* os: Windows
* os: Linux
* os: macOS


### Issue life cycle

```mermaid
graph TD
    input[/issue created/] -->
    needs-triage
    needs-triage --triage--> close(wont-implement, wont-fix, duplicate, invalid)

    needs-triage --triage--> wait-for-implementation
    needs-triage --triage--> wait-for-response

    wait-for-response --response--> needs-triage

    wait-for-implementation --PR-created--> pr-created --PR-merged--> output[/close/]

    close --> output[/close/]
```

### Pull request life cycle

```mermaid
flowchart TD
    input[/pull request created/] -->
    wait-for-review
    --start reviewing -->
    reviewing
    --finish review -->
    reviewed{approved}

    reviewed --Y-->
    wait-for-merge -->
    output[/merge/]

    reviewed --n-->
    require-more-information{require more information}

    require-more-information --y-->
    wait-for-response
    --response-->
    require-more-information

    require-more-information --n-->
    wait-for-modification
    --modification-received-->
    review
```


[conventional-commits]: https://www.conventionalcommits.org/
