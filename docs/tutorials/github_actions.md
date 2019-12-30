## Create new release with Github Actions

### Automatic bumping of version

In order to execute `cz bump` in your CI, and push the new commit and
the new tag, back to your master branch, we have to:
1. Create a personal access token. [Follow the instructions here](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line#creating-a-token). And copy the generated key
2. Create a secret called `PERSONAL_ACCESS_TOKEN`, with the copied key, by going to your
project repository and then `Settings > Secrets > Add new secret`.
3. In your repostiroy create a new file `.github/workflows/bumpversion.yml`
with the following content.

```yaml
name: Bump version

on:
  push:
    branches:
      - master  # another branch could be specified here

jobs:
  build:
    if: "!contains(github.event.head_commit.message, 'bump')"
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.x']
    steps:
    - uses: actions/checkout@v2
      with:
        token: '${{ secrets.PERSONAL_ACCESS_TOKEN }}'
        fetch-depth: 0
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python --version
        python -m pip install -U commitizen
    - name: Create bump
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        cz bump --yes
    - name: Push changes
      uses: Woile/github-push-action@master
      with:
        github_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
        tags: "true"
```

Push to master and that's it.

### Publishing a python package

Once the new tag is created, triggering an automatic publish command would be desired.

In order to do so, first 2 secrets need to be added with the information
of our pypi account.

Go to `Settings > Secrets > Add new secret` and add the secrets: `PYPI_USERNAME` and `PYPI_PASSWORD`.

Create a file in `.github/workflows/pythonpublish.yaml` with the following content:

```yaml
name: Upload Python Package

on:
  push:
    tags:
      - '*' # Will trigger for every tag, alternative: 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v1
    - name: Set up Python
      uses: actions/setup-python@v1
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --pre -U poetry
        poetry --version
        poetry install
    - name: Build and publish
      env:
        PYPI_USERNAME: ${{ secrets.PYPI_USERNAME }}
        PYPI_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: |
        ./scripts/publish
```

Notice that we are calling a bash script in `./scripts/publish`, you should
configure it with your tools (twine, poetry, etc). Check [commitizen example](https://github.com/Woile/commitizen/blob/master/scripts/publish)

Push the changes and that's it.