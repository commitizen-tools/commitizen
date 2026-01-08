## Create a new release with GitHub Actions

This guide shows you how to automatically bump versions, create changelogs, and publish releases using Commitizen in GitHub Actions.

### Prerequisites

Before setting up the workflow, you'll need:

1. A personal access token with repository write permissions
2. Commitizen configured in your project (see [configuration documentation](../config/configuration_file.md))

### Automatic version bumping

To automatically execute `cz bump` in your CI and push the new commit and tag back to your repository, follow these steps:

#### Step 1: Create a personal access token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Commitizen CI")
4. Select the `repo` scope to grant full repository access
5. Click "Generate token" and **copy the token immediately** (you won't be able to see it again)

!!! warning "Important: Use Personal Access Token, not GITHUB_TOKEN"
    If you use `GITHUB_TOKEN` instead of `PERSONAL_ACCESS_TOKEN`, the workflow won't trigger another workflow run. This is a GitHub security feature to prevent infinite loops. The `GITHUB_TOKEN` is treated like using `[skip ci]` in other CI systems.

#### Step 2: Add the token as a repository secret

1. Go to your repository on GitHub
2. Navigate to `Settings > Secrets and variables > Actions`
3. Click "New repository secret"
4. Name it `PERSONAL_ACCESS_TOKEN`
5. Paste the token you copied in Step 1
6. Click "Add secret"

#### Step 3: Create the workflow file

Create a new file `.github/workflows/bumpversion.yml` in your repository with the following content:

```yaml title=".github/workflows/bumpversion.yml"
name: Bump version

on:
  push:
    branches:
      - master  # or 'main' if that's your default branch

jobs:
  bump-version:
    if: "!startsWith(github.event.head_commit.message, 'bump:')"
    runs-on: ubuntu-latest
    name: "Bump version and create changelog with commitizen"
    steps:
      - name: Check out
        uses: actions/checkout@v6
        with:
          token: "${{ secrets.PERSONAL_ACCESS_TOKEN }}"
          fetch-depth: 0
      - name: Create bump and changelog
        uses: commitizen-tools/commitizen-action@master
        with:
          github_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

#### How it works

- **Trigger**: The workflow runs on every push to the `master` branch (or `main` if you change it)
- **Conditional check**: The `if` condition prevents infinite loops by skipping the job if the commit message starts with `bump:`
- **Checkout**: Uses your personal access token to check out the repository with full history (`fetch-depth: 0`)
- **Bump**: The `commitizen-action` automatically:
    - Determines the version increment based on your commit messages
    - Updates version files (as configured in your `pyproject.toml` or other config)
    - Creates a new git tag
    - Generates/updates the changelog
    - Pushes the commit and tag back to the repository

Once you push this workflow file to your repository, it will automatically run on the next push to your default branch.

Check out [commitizen-action](https://github.com/commitizen-tools/commitizen-action) for more details.

### Creating a GitHub release

To automatically create a GitHub release when a new version is bumped, you can extend the workflow above.

The `commitizen-action` creates an environment variable called `REVISION` containing the newly created version. You can use this to create a release with the changelog content.

```yaml title=".github/workflows/bumpversion.yml"
name: Bump version

on:
  push:
    branches:
      - master  # or 'main' if that's your default branch

jobs:
  bump-version:
    if: "!startsWith(github.event.head_commit.message, 'bump:')"
    runs-on: ubuntu-latest
    name: "Bump version and create changelog with commitizen"
    steps:
      - name: Check out
        uses: actions/checkout@v6
        with:
          token: "${{ secrets.PERSONAL_ACCESS_TOKEN }}"
          fetch-depth: 0
      - name: Create bump and changelog
        uses: commitizen-tools/commitizen-action@master
        with:
          github_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          changelog_increment_filename: body.md
      - name: Release
        uses: ncipollo/release-action@v1
        with:
          tag: v${{ env.REVISION }}
          bodyFile: "body.md"
          skipIfReleaseExists: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

You can find the complete workflow in our repository at [bumpversion.yml](https://github.com/commitizen-tools/commitizen/blob/master/.github/workflows/bumpversion.yml).

### Publishing a Python package

After a new version tag is created by the bump workflow, you can automatically publish your package to PyPI.

#### Step 1: Create a PyPI API token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll to the "API tokens" section
3. Click "Add API token"
4. Give it a name (e.g., "GitHub Actions")
5. Set the scope (project-specific or account-wide)
6. Click "Add token" and **copy the token immediately**

!!! tip "Using API tokens"
    PyPI API tokens are more secure than passwords. Use `__token__` as the username and the token as the password.

#### Step 2: Add the token as a repository secret

1. Go to your repository on GitHub
2. Navigate to `Settings > Secrets and variables > Actions`
3. Click "New repository secret"
4. Name it `PYPI_PASSWORD`
5. Paste the PyPI token
6. Click "Add secret"

#### Step 3: Create the publish workflow

Create a new file `.github/workflows/pythonpublish.yml` that triggers on tag pushes:

```yaml title=".github/workflows/pythonpublish.yml"
name: Upload Python Package

on:
  push:
    tags:
      - "*"  # Will trigger for every tag, alternative: 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: latest
          virtualenvs-in-project: true
          virtualenvs-create: true
      - name: Install dependencies
        run: |
          poetry --version
          poetry install
      - name: Build and publish
        env:
          POETRY_HTTP_BASIC_PYPI_USERNAME: __token__
          POETRY_HTTP_BASIC_PYPI_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
        run: poetry publish --build
```

This workflow uses Poetry to build and publish the package. You can find the complete workflow in our repository at [pythonpublish.yml](https://github.com/commitizen-tools/commitizen/blob/master/.github/workflows/pythonpublish.yml).

!!! note "Alternative publishing methods"
    You can also use [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) or other build tools like `setuptools`, `flit`, or `hatchling` to publish your package.
