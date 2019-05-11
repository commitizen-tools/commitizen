# CHANGELOG

## v1.5.0

### Feature

- it is possible to specify a pattern to be matched in configuration `files` when doing bump.

## v1.4.0

### Feature

- new argument (--yes) in bump to accept prompt questions

### Fix

- error is shown when commiting fails.

## v1.3.0

### Feature

- bump: new commit message template, useful when having to skip ci.

## v1.2.1

### Fix

- prefixes like docs, build, etc no longer generate a PATCH

## v1.2.0

### Feature

- custom cz plugins now support bumping version

## v1.1.1

### Fix

- breaking change is now part of the body, instead of being in the subject

## v1.1.0

### Features

- auto bump version based on conventional commits using sem ver
- pyproject support (see [pyproject.toml](./pyproject.toml) for usage)

## v1.0.0

### Features

- more documentation
- added tests
- support for conventional commits 1.0.0

### BREAKING CHANGES

- use of questionary to generate the prompt (so we depend on promptkit 2.0)
- python 3 only
