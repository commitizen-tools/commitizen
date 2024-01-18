## Create a new release with Github Actions

### Automatic bumping of version

To execute `cz bump` in your CI, and push the new commit and
the new tag, back to your master branch, we have to:

1. Create a personal access token. [Follow the instructions here](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line#creating-a-token). And copy the generated key
2. Create a secret called `PERSONAL_ACCESS_TOKEN`, with the copied key, by going to your
   project repository and then `Settings > Secrets > Add new secret`.
3. In your repository create a new file `.github/workflows/bumpversion.yml`
   with the following content.

!!! warning
    If you use `GITHUB_TOKEN` instead of `PERSONAL_ACCESS_TOKEN`, the job won't trigger another workflow. It's like using `[skip ci]` in other CI's.

```yaml
name: Bump version

on:
  push:
    branches:
      - master

jobs:
  bump-version:
    if: "!startsWith(github.event.head_commit.message, 'bump:')"
    runs-on: ubuntu-latest
    name: "Bump version and create changelog with commitizen"
    steps:
      - name: Check out
        uses: actions/checkout@v3
        with:
          token: "${{ secrets.PERSONAL_ACCESS_TOKEN }}"
          fetch-depth: 0
      - name: Create bump and changelog
        uses: commitizen-tools/commitizen-action@master
        with:
          github_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

Push to master and that's it.

### Creating a github release

You can modify the previous action.

Add the variable `changelog_increment_filename` in the `commitizen-action`, specifying
where to output the content of the changelog for the newly created version.

And then add a step using a github action to create the release: `softprops/action-gh-release`

The commitizen action creates an env variable called `REVISION`, containing the
newely created version.

```yaml
- name: Create bump and changelog
  uses: commitizen-tools/commitizen-action@master
  with:
    github_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
    changelog_increment_filename: body.md
- name: Release
  uses: softprops/action-gh-release@v1
  with:
    body_path: "body.md"
    tag_name: ${{ env.REVISION }}
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Publishing a python package

Once the new tag is created, triggering an automatic publish command would be desired.

In order to do so, the credential needs to be added with the information of our PyPI account.

Instead of using username and password, we suggest using [api token](https://pypi.org/help/#apitoken) generated from PyPI.

After generate api token, use the token as the PyPI password and `__token__` as the username.

Go to `Settings > Secrets > Add new secret` and add the secret: `PYPI_PASSWORD`.

Create a file in `.github/workflows/pythonpublish.yaml` with the following content:

```yaml
name: Upload Python Package

on:
  push:
    tags:
      - "*" # Will trigger for every tag, alternative: 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
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
          PYPI_USERNAME: __token__
          PYPI_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
        run: |
          ./scripts/publish
```

Notice that we are using poetry, and we are calling a bash script in `./scripts/publish`. You should configure the action, and the publish with your tools (twine, poetry, etc.). Check [commitizen example](https://github.com/commitizen-tools/commitizen/blob/master/scripts/publish)
You can also use [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) to publish your package.

Push the changes and that's it.
