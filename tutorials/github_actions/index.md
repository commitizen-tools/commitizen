## Create a new release with GitHub Actions

This guide shows you how to automatically bump versions, create changelogs, and publish releases using Commitizen in GitHub Actions.

Tip

Check the new [setup-cz](https://github.com/marketplace/actions/setup-commitizen-cli) action, simple and with [examples](https://github.com/commitizen-tools/setup-cz/tree/main/examples)

### Prerequisites

Before setting up the workflow, you'll need:

1. A personal access token with repository write permissions
1. Commitizen configured in your project (see [configuration documentation](https://commitizen-tools.github.io/commitizen/config/configuration_file/index.md))

### Automatic Version Bumping

To automatically execute `cz bump` in your CI and push the new commit and tag back to your repository, follow these steps:

#### Step 1: Create a Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
1. Click "Generate new token (classic)"
1. Give it a descriptive name (e.g., "Commitizen CI")
1. Select the `repo` scope to grant full repository access
1. Click "Generate token" and **copy the token immediately** (you won't be able to see it again)

Important: Use Personal Access Token, not GITHUB_TOKEN

If you use `GITHUB_TOKEN` instead of `PERSONAL_ACCESS_TOKEN`, the workflow won't trigger another workflow run. This is a GitHub security feature to prevent infinite loops. The `GITHUB_TOKEN` is treated like using `[skip ci]` in other CI systems.

#### Step 2: Add the Token as a Repository Secret

1. Go to your repository on GitHub
1. Navigate to `Settings > Secrets and variables > Actions`
1. Click "New repository secret"
1. Name it `PERSONAL_ACCESS_TOKEN`
1. Paste the token you copied in Step 1
1. Click "Add secret"

#### Step 3: Create the Workflow File

Create a new file `.github/workflows/bump-version.yml` in your repository with the following content:

.github/workflows/bump-version.yml

```
name: Bump version

on:
  push:
    branches:
      - main

jobs:
  bump:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: write
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
          fetch-tags: true
      - uses: commitizen-tools/setup-cz@main
        with:
          python-version: "3.x"
      - id: bump-version
        run: |
          old_sha="$(git rev-parse HEAD)"

          cz --no-raise 21 bump --yes --annotated-tag

          if [ "$(git rev-parse HEAD)" = "$old_sha" ]; then
            echo "No bump-eligible commits found, skipping release."
            echo "bumped=false" >> $GITHUB_OUTPUT
            exit 0
          fi

          echo "bumped=true" >> $GITHUB_OUTPUT
          git push --follow-tags
          new_version="$(cz version -p)"
          echo "new_version=$new_version" >> $GITHUB_OUTPUT
          new_version_tag="$(cz version -p --tag)"
          echo "new_version_tag=$new_version_tag" >> $GITHUB_OUTPUT
      - name: Github Release
        if: steps.bump-version.outputs.bumped == 'true'
        env:
          GH_TOKEN: ${{ github.token }}
          NEW_VERSION: ${{ steps.bump-version.outputs.new_version }}
          NEW_VERSION_TAG: ${{ steps.bump-version.outputs.new_version_tag }}
        run: |
          gh release create "${NEW_VERSION_TAG}" --notes-file .changelog.md
          cz changelog --dry-run "${NEW_VERSION}" > .changelog.md
```

#### How it works

- The action will trigger the workflow on every push to the `main` branch.
- The job requests `contents: write` and `actions: write` so it can push the bump commit and tag, and trigger dependent workflows.
- **Setup**: The `setup-cz` action installs the Commitizen CLI with the requested Python version
- **Bump**: The `cz bump --yes --annotated-tag` command automatically:
  - Determines the version increment based on your commit messages
  - Updates version files (as configured in your `pyproject.toml` or other config)
  - Creates a new annotated git tag
  - Generates/updates the changelog
- **Push**: `git push --follow-tags` pushes the bump commit along with the new tag back to the repository
- **Github Release**: creates a Github Release

Once you push this workflow file to your repository, it will automatically run on the next push to your default branch.

Check out [commitizen-tools/setup-cz](https://github.com/commitizen-tools/setup-cz) for more details.

### Previewing the Version Bump on Pull Requests

To help reviewers spot unexpected version bumps before merging, you can run `cz version -p` on every pull request and post (or update) a sticky comment summarizing the would-be version bump.

Create `.github/workflows/pr-bump-preview.yml`:

.github/workflows/pr-bump-preview.yml

````
name: PR bump preview

on:
  pull_request_target:
    types: [opened, reopened, synchronize, ready_for_review]

permissions:
  contents: read
  pull-requests: write

jobs:
  bump-preview:
    # Skip drafts and fork PRs (see "How it works" below).
    if: >
      ${{
        github.event.pull_request.draft == false &&
        github.event.pull_request.head.repo.full_name ==
          github.event.pull_request.base.repo.full_name
      }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
          fetch-tags: true
          persist-credentials: false
      - uses: commitizen-tools/setup-cz@main
        with:
          python-version: "3.x"
          set-git-config: false
      - name: Run cz version
        id: dry-run
        run: |
          set +e
          output="$(cz version -p --next 2>&1)"
          status=$?
          set -e
          {
            echo "status=${status}"
            echo "output<<__CZ_BUMP_PREVIEW__"
            printf '%s\n' "${output}"
            echo "__CZ_BUMP_PREVIEW__"
          } >> "$GITHUB_OUTPUT"
      - name: Build comment body
        env:
          STATUS: ${{ steps.dry-run.outputs.status }}
          OUTPUT: ${{ steps.dry-run.outputs.output }}
        run: |
          {
            echo "<!-- commitizen-bump-preview -->"
            echo "## 🔍 Commitizen bump preview"
            echo ""
            case "${STATUS}" in
              0)
                echo "Merging this PR will produce the following bump:"
                echo ""
                echo '```'
                printf '%s\n' "${OUTPUT}"
                echo '```'
                ;;
              21)
                echo "No commits in this PR are eligible for a version bump."
                ;;
              *)
                echo "⚠️ \`cz bump --dry-run\` exited with status \`${STATUS}\`:"
                echo ""
                echo '```'
                printf '%s\n' "${OUTPUT}"
                echo '```'
                ;;
            esac
          } > comment.md
      - name: Find existing preview comment
        id: find-comment
        uses: peter-evans/find-comment@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          issue-number: ${{ github.event.pull_request.number }}
          comment-author: "github-actions[bot]"
          body-includes: "<!-- commitizen-bump-preview -->"
      - uses: peter-evans/create-or-update-comment@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          comment-id: ${{ steps.find-comment.outputs.comment-id }}
          issue-number: ${{ github.event.pull_request.number }}
          body-path: comment.md
          edit-mode: replace
````

You can find the complete workflow in our repository at [pr-bump-preview.yml](https://github.com/commitizen-tools/commitizen/blob/master/.github/workflows/pr-bump-preview.yml).

### Publishing a Python Package

After a new version tag is created by the bump workflow, you can automatically publish your package to PyPI.

#### Step 1: Create a PyPI API token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
1. Scroll to the "API tokens" section
1. Click "Add API token"
1. Give it a name (e.g., "GitHub Actions")
1. Set the scope (project-specific or account-wide)
1. Click "Add token" and **copy the token immediately**

Using trusted publishing (recommended)

Instead of API tokens, consider using [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) with OpenID Connect (OIDC). This is more secure as it doesn't require storing secrets. The `pypa/gh-action-pypi-publish` action supports trusted publishing when you configure it in your PyPI project settings.

#### Step 2: Add the token as a repository secret

1. Go to your repository on GitHub
1. Navigate to `Settings > Secrets and variables > Actions`
1. Click "New repository secret"
1. Name it `PYPI_PASSWORD`
1. Paste the PyPI token
1. Click "Add secret"

#### Step 3: Create the Publish Workflow

Create a new file `.github/workflows/pythonpublish.yml` that triggers on tag pushes:

.github/workflows/pythonpublish.yml

```
name: Upload Python Package

on:
  push:
    tags:
      - "*"  # Will trigger for every tag, alternative: 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.x"
      - name: Install the latest version of uv
        uses: astral-sh/setup-uv@v10
      - name: publish
        run: |
          uv sync
          uv publish --username "${PYPI_USERNAME}" --password "${PYPI_PASSWORD}"
```

This workflow uses uv to build and publish the package. You can find the complete workflow in our repository at [pythonpublish.yml](https://github.com/commitizen-tools/commitizen/blob/master/.github/workflows/pythonpublish.yml).

Alternative publishing methods

You can also use [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) or other build tools like `setuptools`, `flit`, or `hatchling` to publish your package.
