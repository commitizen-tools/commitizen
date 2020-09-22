## Unreleased

### Fix

- **#271**: add annotated_tag option to bump

## v2.4.0 (2020-09-18)

### Feat

- **cz_check**: cz check can read commit message from pipe

## v2.3.1 (2020-09-07)

### Fix

- conventional commit schema

## v2.3.0 (2020-09-03)

### Fix

- **cli**: add guideline for subject input
- **cli**: wrap the word enter with brackets

### Feat

- **cli**: rewrite cli instructions to be more succinct about what they require

## v2.2.0 (2020-08-31)

### Feat

- **cz_check**: cz check can read from a string input

## v2.1.0 (2020-08-06)

### Refactor

- **cz_check**: Refactor _get_commits to return GitCommit instead of dict

### Feat

- **cz_check**: Add rev to all displayed ill-formatted commits
- **cz_check**: Update to show all ill-formatted commits

## v2.0.2 (2020-08-03)

### Fix

- **git**: use double quotation mark in get_tags

## v2.0.1 (2020-08-02)

### Fix

- **commands/changelog**: add exception message when failing to find an incremental revision
- **commands/bump**: display message variable properly

## v2.0.0 (2020-07-26)

### Fix

- add missing `pyyaml` dependency
- **cli**: make command required for commitizen

### Feat

- **init**: enable setting up pre-commit hook through "cz init"

### Refactor

- **config**: drop "files" configure support. Please use "version_files" instead
- **config**: remove ini configuration support
- **cli**: remove "--version" argument

### BREAKING CHANGE

- setup.cfg, .cz and .cz.cfg are no longer supported
- Use "cz verion" instead
- "cz --debug" will no longer work

## v1.25.0 (2020-07-26)

### Feat

- **conventional_commits**: use and proper support for conventional commits v1.0.0

## v1.24.0 (2020-07-26)

### Feat

- add author and author_email to git commit

## v1.23.4 (2020-07-26)

### Refactor

- **changelog**: remove pkg_resources dependency

## v1.23.3 (2020-07-25)

### Fix

- **commands/bump**: use `return_code` in commands used by bump

## v1.23.2 (2020-07-25)

### Fix

- **bump**: add changelog file into stage when running `cz bump --changelog`
- **commands/commit**: use return_code to raise commit error, not stderr

### Refactor

- **cmd**: add return code to Command

## v1.23.1 (2020-07-14)

### Fix

- Raise NotAGitProjectError only in git related command

## v1.23.0 (2020-06-14)

### Refactor

- **exception**: rename MissingConfigError as MissingCzCustomizeConfigError
- **exception**: Rename CommitFailedError and TagFailedError with Bump prefix
- **commands/init**: add test case and remove unaccessible code
- **exception**: move output message related to exception into exception
- **exception**: implement message handling mechanism for CommitizenException

### Feat

- **cli**: enable displaying all traceback for CommitizenException when --debug flag is used

## v1.22.3 (2020-06-10)

### Refactor

- **cli**: do not show traceback if the raised exception is CommitizenException
- introduce DryRunExit, ExpectedExit, NoCommandFoundError, InvalidCommandArgumentError
- use custom exception for error handling
- **error_codes**: remove unused NO_COMMIT_MSG error code

## v1.22.2 (2020-05-29)

### Fix

- **changelog**: empty lines at the beginning of the CHANGELOG

## v1.22.1 (2020-05-23)

### Fix

- **templates**: remove trailing space in keep_a_changelog

## v1.22.0 (2020-05-13)

### Fix

- **changelog**: rename `message_hook` -> `changelog_message_builder_hook`

### Feat

- **changelog**: add support for `changelog_hook` when changelog finishes the generation
- **changelog**: add support for `message_hook` method
- **changelog**: add support for modifying the change_type in the title of the changelog

## v1.21.0 (2020-05-09)

### Feat

- **commands/bump**: add "--check-consistency" optional

## v1.20.0 (2020-05-06)

### Feat

- **bump**: add optional --no-verify argument for bump command

## v1.19.3 (2020-05-04)

### Fix

- **docs**: change old url woile.github.io to commitizen-tools.github.io
- **changelog**: generate today's date when using an unreleased_version

## v1.19.2 (2020-05-03)

### Fix

- **changelog**: sort the commits properly to their version

## v1.19.1 (2020-05-03)

### Fix

- **commands/check**: Show warning if no commit to check when running `cz check --rev-range`

### Refactor

- **cli**: add explicit category for deprecation warnings

## v1.19.0 (2020-05-02)

### Fix

- **git**: missing dependency removed
- **changelog**: check get_metadata for existing changelog file

### Feat

- **changelog**: add support for any commit rule system
- **changelog**: add incremental flag

## v1.18.3 (2020-04-22)

### Refactor

- **commands/init**: fix typo

## v1.18.2 (2020-04-22)

### Refactor

- **git**: replace GitCommit.message code with one-liner
- **changelog**: use functions from changelog.py
- **changelog**: rename category to change_type to fit 'keep a changelog'
- **templates**: rename as "keep_a_changelog_template.j2"
- **templates**: remove unneeded __init__ file
- **cli**: reorder commands
- **templates**: move changelog_template from cz to templates
- **tests/utils**: move create_file_and_commit to tests/utils
- **commands/changelog**: remove redundant if statement
- **commands/changelog**: use jinja2 template instead of string concatenation to build changelog

### Fix

- **git**: fix returned value for GitCommit.message when body is empty
- **cz/conventional_commits**: fix schema_pattern break due to rebase
- **changelog_template**: fix list format
- **commitizen/cz**: set changelog_map, changelog_pattern to none as default
- **commands/changelog**: remove --skip-merge argument
- **cli**: add changelog arguments

### Feat

- **commands/changelog**: make changelog_file an option in config
- **commands/changelog**: exit when there is no commit exists
- **commands/changlog**: add --start-rev argument to `cz changelog`
- **changelog**: generate changelog based on git log
- **commands/changelog**: generate changelog_tree from all past commits
- **cz/conventinal_commits**: add changelog_map, changelog_pattern and implement process_commit
- **cz/base**: add default process_commit for processing commit message
- **changelog**: changelog tree generation from markdown

## v1.18.1 (2020-04-16)

### Fix

- **config**: display ini config deprecation warning only when commitizen config is inside

## v1.18.0 (2020-04-13)

### Refactor

- **cz/customize**: remove unused mypy ignore
- **mypy**: fix mypy check by checking version.pre exists
- **cz**: add type annotation to registry
- **commands/check**: fix type annotation
- **config/base**: use Dict to replace dict in base_config
- **cz/base**: fix config type used in base cz
- **cz**: add type annotation for each function in cz
- **config**: fix mypy warning for _conf

### Fix

- **cz/customize**: add error handling when customize detail is not set

### Feat

- **bump**: support for ! as BREAKING change in commit message

## v1.17.1 (2020-03-24)

### Fix

- **commands/check**: add help text for check command without argument

### Refactor

- **cli**: fix typo

## v1.17.0 (2020-03-15)

### Refactor

- **tests/bump**: use parameterize to group similliar tests
- **cz/connventional_commit**: use \S to check scope
- **git**: remove unnecessary dot between git range

### Fix

- **bump**: fix bump find_increment error

### Feat

- **commands/check**: add --rev-range argument for checking commits within some range

## v1.16.4 (2020-03-03)

### Fix

- **commands/init**: fix clean up file when initialize commitizen config

### Refactor

- **defaults**: split config files into long term support and deprecated ones

## v1.16.3 (2020-02-20)

### Fix

- replace README.rst with docs/README.md in config files

### Refactor

- **docs**: remove README.rst and use docs/README.md

## v1.16.2 (2020-02-01)

### Fix

- **commands/check**: add bump into valid commit message of convention commit pattern

## v1.16.1 (2020-02-01)

### Fix

- **pre-commit**: set pre-commit check stage to commit-msg

## v1.16.0 (2020-01-21)

### Refactor

- **commands/bump**: rename parameter into bump_setting to distinguish bump_setting and argument
- **git**: rename get tag function to distinguish return str and GitTag
- **cmd**: reimplement how cmd is run
- **git**: Use GitCommit, GitTag object to store commit and git information
- **git**: make arguments other then start and end in get_commit keyword arguments
- **git**: Change get_commits into returning commits instead of lines of messsages

### Feat

- **git**: get_commits default from first_commit

## v1.15.1 (2020-01-20)

## v1.15.0 (2020-01-20)

### Refactor

- **tests/commands/bump**: use tmp_dir to replace self implemented tmp dir behavior
- **git**: make find_git_project_root return None if it's not a git project
- **config/base_config**: make set_key not implemented
- **error_codes**: move all the error_codes to a module
- **config**: replace string type path with pathlib.Path
- **test_bump_command**: rename camel case variables
- **tests/commands/check**: use pytest fixture tmpdir replace self implemented contextmanager
- **test/commands/other**: replace unit test style mock with mocker fixture
- **tests/commands**: separate command unit tests into modules
- **tests/commands**: make commands related tests a module

### Fix

- **git**: remove breakline in the return value of find_git_project_root
- **cli**: fix --version not functional

### Feat

- **config**: look up configuration in git project root
- **git**: add find_git_project_root

## v1.14.2 (2020-01-14)

### Fix

- **github_workflow/pythonpublish**: use peaceiris/actions-gh-pages@v2 to publish docs

## v1.14.1 (2020-01-11)

## v1.14.0 (2020-01-06)

### Refactor

- **pre-commit-hooks**: add metadata for the check hook

### Feat

- **pre-commit-hooks**: add pre-commit hook

### Fix

- **cli**: fix the way default handled for name argument
- **cli**: fix name cannot be overwritten through config in newly refactored config design

## v1.13.1 (2019-12-31)

### Fix

- **github_workflow/pythonpackage**: set git config for unit testing
- **scripts/test**: ensure the script fails once the first failure happens

## v1.13.0 (2019-12-30)

### Feat

- add project version to command init

## v1.12.0 (2019-12-30)

### Feat

- new init command

## v1.10.3 (2019-12-29)

### Refactor

- **commands/bump**: use "version_files" internally
- **config**: set "files" to alias of "version_files"

## v1.10.2 (2019-12-27)

### Refactor

- new config system where each config type has its own class
- **config**: add type annotation to config property
- **config**: fix wrongly type annoated functions
- **config/ini_config**: move deprecation warning into class initialization
- **config**: use add_path instead of directly assigning _path
- **all**: replace all the _settings invoke with settings.update
- **cz/customize**: remove unnecessary statement "raise NotImplementedError("Not Implemented yet")"
- **config**: move default settings back to defaults
- **config**: Make config a class and each type of config (e.g., toml, ini) a child class

### Fix

- **config**: handle empty config file
- **config**: fix load global_conf even if it doesn't exist
- **config/ini_config**: replase outdated _parse_ini_settings with _parse_settings

## v1.10.1 (2019-12-10)

### Fix

- **cli**: overwrite "name" only when it's not given
- **config**: fix typo

## v1.10.0 (2019-11-28)

### Feat

- support for different commitizens in `cz check`
- **bump**: new argument --files-only

## v1.9.2 (2019-11-23)

### Fix

- **commands/check.py**: --commit-msg-file is now a required argument

## v1.9.1 (2019-11-23)

### Fix

- **cz/exceptions**: exception AnswerRequiredException not caught (#89)

## v1.9.0 (2019-11-22)

### Feat

- **Commands/check**: enforce the project to always use conventional commits
- **config**: add deprecation warning for loading config from ini files
- **cz/customize**: add jinja support to enhance template flexibility
- **cz/filters**: add required_validator and multiple_line_breaker
- **cz/cz_customize**: implement info to support info and info_path
- **cz/cz_customize**: enable bump_pattern bump_map customization
- **cz/cz_customize**: implement customizable cz
- **Commands/commit**: add ´--dry-run´ flag to the Commit command
- new 'git-cz' entrypoint

### Refactor

- **config**: remove has_pyproject which is no longer used
- **cz/customize**: make jinja2 a custom requirement. if not installed use string.Tempalte instead
- **cz/utils**: rename filters as utils
- **cli**: add back --version and remove subcommand required constraint

### Fix

- commit dry-run doesnt require staging to be clean
- correct typo to spell "convention"
- removing folder in windows throwing a PermissionError
- **scripts**: add back the delelte poetry prefix
- **test_cli**: testing the version command

## v1.8.0 (2019-11-12)

### Fix

- **commands/commit**: catch exception raised by customization cz
- **cli**: handle the exception that command is not given
- **cli**: enforce subcommand as required

### Refactor

- **cz/conventional_commit**: make NoSubjectException inherit CzException and add error message
- **command/version**: use out.write instead of out.line
- **command**: make version a command instead of an argument

### Feat

- **cz**: add a base exception for cz customization
- **commands/commit**: abort commit if there is nothing to commit
- **git**: add is_staging_clean to check if there is any file in git staging

## v1.7.0 (2019-11-08)

### Fix

- **cz**: fix bug in BaseCommitizen.style
- **cz**: fix merge_style usage error
- **cz**: remove breakpoint

### Refactor

- **cz**: change the color of default style

### Feat

- **config**: update style instead of overwrite
- **config**: parse style in config
- **commit**: make style configurable for commit command

## v1.6.0 (2019-11-05)

### Feat

- **commit**: new retry argument to execute previous commit again

## v1.5.1 (2019-06-04)

### Fix

- #28 allows poetry add on py36 envs

## v1.5.0 (2019-05-11)

### Feat

- **bump**: it is now possible to specify a pattern in the files attr to replace the version

## v1.4.0 (2019-04-26)

### Fix

- **bump**: handle commit and create tag failure

### Feat

- added argument yes to bump in order to accept questions

## v1.3.0 (2019-04-24)

### Feat

- **bump**: new commit message template

## v1.2.1 (2019-04-21)

### Fix

- **bump**: prefixes like docs, build, etc no longer generate a PATCH

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

## v0.9.1 (2017-11-11)

### Fix

- **setup.py**: future is now required for every python version

## v0.9.0 (2017-11-08)

### Refactor

- python 2 support

## v0.8.6 (2017-11-08)

## v0.8.5 (2017-11-08)

## v0.8.4 (2017-11-08)

## v0.8.3 (2017-11-08)

## v0.8.2 (2017-10-08)

## v0.8.1 (2017-10-08)

## v0.8.0 (2017-10-08)

### Feat

- **cz**: jira smart commits

## v0.7.0 (2017-10-08)

### Refactor

- **cli**: renamed all to ls command
- **cz**: renamed angular cz to conventional changelog cz

## v0.6.0 (2017-10-08)

### Feat

- info command for angular

## v0.5.0 (2017-10-07)

## v0.4.0 (2017-10-07)

## v0.3.0 (2017-10-07)

## v0.2.0 (2017-10-07)

### Feat

- **config**: new loads from ~/.cz and working project .cz .cz.cfg and setup.cfg
- package discovery

### Refactor

- **cz_angular**: improved messages
