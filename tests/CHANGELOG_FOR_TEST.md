
## v1.2.0 (2019-04-19)

### feat

- custom cz plugins now support bumping version

## v1.1.1 (2019-04-18)

### refactor

- changed stdout statements
- **schema**: command logic removed from commitizen base
- **info**: command logic removed from commitizen base
- **example**: command logic removed from commitizen base
- **commit**: moved most of the commit logic to the commit command

### fix

- **bump**: commit message now fits better with semver
- conventional commit 'breaking change' in body instead of title

## v1.1.0 (2019-04-14)

### feat

- new working bump command
- create version tag
- update given files with new version
- **config**: new set key, used to set version to cfg
- support for pyproject.toml
- first semantic version bump implementation

### fix

- removed all from commit
- fix config file not working

### refactor

- added commands folder, better integration with decli

## v1.0.0 (2019-03-01)

### refactor

- removed delegator, added decli and many tests

### BREAKING CHANGE

- API is stable

## 1.0.0b2 (2019-01-18)

## v1.0.0b1 (2019-01-17)

## user_def (2019-01-10)

### feat

- py3 only, tests and conventional commits 1.0

## v0.9.11 (2018-12-17)

### fix

- **config**: load config reads in order without failing if there is no commitizen section

## v0.9.10 (2018-09-22)

### fix

- parse scope (this is my punishment for not having tests)

## v0.9.9 (2018-09-22)

### fix

- parse scope empty

## v0.9.8 (2018-09-22)

### fix

- **scope**: parse correctly again

## v0.9.7 (2018-09-22)

### fix

- **scope**: parse correctly

## v0.9.6 (2018-09-19)

### refactor

- **conventionalCommit**: moved filters to questions instead of message

### fix

- **manifest**: included missing files

## v0.9.5 (2018-08-24)

### fix

- **config**: home path for python versions between 3.0 and 3.5

## v0.9.4 (2018-08-02)

### feat

- **cli**: added version

## v0.9.3 (2018-07-28)

### feat

- **committer**: conventional commit is a bit more intelligent now

## v0.9.2 (2017-11-11)

### refactor

- renamed conventional_changelog to conventional_commits, not backward compatible

## v0.9.1 (2017-11-11)

### fix

- **setup.py**: future is now required for every python version
