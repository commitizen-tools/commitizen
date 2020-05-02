
## v1.2.0 (2019-04-19)

### Feat

- custom cz plugins now support bumping version

## v1.1.1 (2019-04-18)

### Refactor

- changed stdout statements
- **schema**: command logic removed from commitizen base
- **info**: command logic removed from commitizen base
- **example**: command logic removed from commitizen base
- **commit**: moved most of the commit logic to the commit command

### Fix

- **bump**: commit message now fits better with semver
- conventional commit 'breaking change' in body instead of title

## v1.1.0 (2019-04-14)

### Feat

- new working bump command
- create version tag
- update given files with new version
- **config**: new set key, used to set version to cfg
- support for pyproject.toml
- first semantic version bump implementaiton

### Fix

- removed all from commit
- fix config file not working

### Refactor

- added commands folder, better integration with decli

## v1.0.0 (2019-03-01)

### Refactor

- removed delegator, added decli and many tests

### Breaking Change

- API is stable

## 1.0.0b2 (2019-01-18)

## v1.0.0b1 (2019-01-17)

### Feat

- py3 only, tests and conventional commits 1.0

## v0.9.11 (2018-12-17)

### Fix

- **config**: load config reads in order without failing if there is no commitizen section

## v0.9.10 (2018-09-22)

### Fix

- parse scope (this is my punishment for not having tests)

## v0.9.9 (2018-09-22)

### Fix

- parse scope empty

## v0.9.8 (2018-09-22)

### Fix

- **scope**: parse correctly again

## v0.9.7 (2018-09-22)

### Fix

- **scope**: parse correctly

## v0.9.6 (2018-09-19)

### Refactor

- **conventionalCommit**: moved fitlers to questions instead of message

### Fix

- **manifest**: inluded missing files

## v0.9.5 (2018-08-24)

### Fix

- **config**: home path for python versions between 3.0 and 3.5

## v0.9.4 (2018-08-02)

### Feat

- **cli**: added version

## v0.9.3 (2018-07-28)

### Feat

- **commiter**: conventional commit is a bit more intelligent now

## v0.9.2 (2017-11-11)

### Refactor

- renamed conventional_changelog to conventional_commits, not backward compatible

## v0.9.1 (2017-11-11)

### Fix

- **setup.py**: future is now required for every python version
