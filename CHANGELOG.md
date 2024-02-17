
## v3.15.0 (2024-02-17)

### Feat

- **bump**: functionality to add build-metadata to version string

## v3.14.1 (2024-02-04)

### Fix

- **bump**: remove unused method
- **scm**: only search tags that are reachable by the current commit

## v3.14.0 (2024-02-01)

### Feat

- properly bump versions between prereleases (#799)

## v3.13.0 (2023-12-03)

### Feat

- **commands-bump**: automatically create annotated tag if message is given
- add tag message argument to cli
- **git**: add get tag message function
- add custom message to annotated git tag

### Fix

- **test-bump-command**: typo in --annotated-tag option inside test
- **commitizen-git**: add quotes for tag message

### Refactor

- **commands-bump**: make changelog variable in 1 line
- **commands-bump**: cast str to bool

## v3.12.0 (2023-10-18)

### Feat

- **formats**: expose some new customizable changelog formats on the `commitizen.changelog_format` endpoint (Textile, AsciiDoc and RestructuredText)
- **template**: add `changelog --export-template` command
- **template**: allow to override the template from cli, configuration and plugins

### Fix

- **filename**: ensure `file_name` can be passed to `changelog` from `bump` command

## v3.11.0 (2023-10-17)

### Feat

- **cli.py**: Added support for extra git CLI args after -- separator for `cz commit` command

### Refactor

- **git.py**: Removed 'extra_args' from git.commit
- **extra_args**: Fixed broken code due to rebase and finalized tests
- Code Review - round 1 changes
- **Commit**: Added deprecation on git signoff mechanic

## v3.10.1 (2023-10-14)

### Fix

- **bump**: add bump support with custom type + scope + exclamation mark
- **bump**: version bumping

## v3.10.0 (2023-09-25)

### Feat

- Drop support for Python 3.7 (#858)

## v3.9.1 (2023-09-22)

### Fix

- **conf**: handle parse error when init (#856)

## v3.9.0 (2023-09-15)

### Feat

- **commands**: add arg of cz commit to execute git add

### Fix

- **tests**: modify the arg of commit from add to all
- **commitizen**: Modify the function of the arg a of commit from git add all to git add update

### Refactor

- **commitizen**: add return type hint of git add function

## v3.8.2 (2023-09-09)

### Refactor

- **provider**: split provider code and related tests into individual files for maintainability (#830)

## v3.8.1 (2023-09-08)

### Fix

- add sponsors to README

## v3.8.0 (2023-09-05)

### Feat

- **defaults.py**: add always_signoff config option for commits

## v3.7.1 (2023-09-04)

### Fix

- empty error on bump failure

## v3.7.0 (2023-08-26)

### Feat

- **provider**: add npm2 provider to update package.json, package-lock.json, and npm-shrinkwrap.json

### Fix

- **provider**: fix npm version provider to update package-lock.json and npm-shrinkwrap.json if they exist
- **provider**: fix npm provider to update package-lock.json and npm-shrinkwrap.json if they exist
- **test**: pass correct type to get_package_version tests
- **tests**: completed test coverage for npm2

## v3.6.0 (2023-08-01)

### Feat

- **changelog.py**: add encoding to get_metadata
- **unicode**: add unicode support

### Fix

- add missing `encoding` parameter
- **out.py**: `TextIOWrapper.reconfigure` typing
- correct type hinting
- use base config for encoding

### Refactor

- **defaults.py**: use variables in `DEFAULT_SETTINGS`

## v3.5.4 (2023-07-29)

### Refactor

- replace SemVer type literals by respective constants

## v3.5.3 (2023-07-15)

### Fix

- Treat $version the same as unset tag_format in ScmProvider

### Refactor

- Make tag_format properly default to $version

## v3.5.2 (2023-06-25)

### Fix

- **typing**: no_raise is declared as optional

## v3.5.1 (2023-06-24)

### Fix

- only use version tags when generating a changelog

## v3.5.0 (2023-06-23)

### Feat

- Add option in bump command to redirect git output to stderr

## v3.4.1 (2023-06-23)

### Fix

- **veresion_schemes**: import missing Self for python 3.11

## v3.4.0 (2023-06-20)

### Feat

- **version-schemes**: expose `version_schemes` as a `commitizen.scheme` endpoint.

## v3.3.0 (2023-06-13)

### Feat

- add support for cargo workspaces

## v3.2.2 (2023-05-11)

### Fix

- **init**: fix is_pre_commit_installed method

## v3.2.1 (2023-05-03)

### Fix

- add support for importlib_metadata 6

## v3.2.0 (2023-05-01)

### Feat

- **hooks**: add prepare-commit-msg and post-commit hooks
- **commit**: add --write-message-to-file option

### Fix

- **bump**: better match for change_type when finding increment
- **changelog**: breaking change on additional types for conventional commits
- **bump**: breaking changes on additional types for conventional commits
- improve errors message when empty .cz.json found
- **init**: poetry detection
- bump decli which is type hinted

### Refactor

- **commit**: change type of write_message_to_file to path

## v3.1.1 (2023-04-28)

### Fix

- bump changelog for prerelease without commits

## v3.1.0 (2023-04-25)

### Feat

- make `major_version_zero` customizable by third parties

## v3.0.1 (2023-04-23)

### Fix

- typo in hook

### Refactor

- set default_install_hook_types

## v3.0.0 (2023-04-23)

### BREAKING CHANGE

- Plugins are now exposed as `commitizen.plugin` entrypoints

### Feat

- **init**: add new settings
- add semver support through version provider new api (#686)
- **changelog**: add merge_prereleases flag
- **providers**: add a `scm` version provider
- **providers**: add support for some JSON-based version providers (NPM, Composer)
- **providers**: add support for some TOML-based versions (PEP621, Poetry, Cargo)
- **providers**: add a `commitizen.provider` endpoint for alternative versions providers
- **plugins**: Switch to an importlib.metadata.EntryPoint-based plugin loading

### Fix

- **init**: welcome message
- small corrections and clean up
- major version zero message
- update dependencies
- **commands/changelog**: use topological order for commit ordering
- **excepthook**: ensure traceback can only be a `TracebackType` or `None`

## v2.42.1 (2023-02-25)

### Fix

- **bump**: fixed environment variables in bump hooks

## v2.42.0 (2023-02-11)

### Feat

- **bump**: support prereleases with start offset

## v2.41.0 (2023-02-08)

### Feat

- **bump**: added support for running arbitrary hooks during bump

## v2.40.0 (2023-01-23)

### Feat

- **yaml_config**: add explicit_start for yaml output

## v2.39.1 (2022-12-31)

### Fix

- filter git diff from commit message

## v2.39.0 (2022-12-31)

### Feat

- **init**: allow user to select which type of pre commit hooks to install

### Fix

- **init**: space between `--hook-type` options
- **init**: report error when hook installation failed

### Refactor

- **init**: `_install_pre_commit_hook` raise error when failed

## v2.38.0 (2022-12-12)

### Feat

- **poetry**: relax packaging version

## v2.37.1 (2022-11-30)

### Fix

- **changelog**: allow rev range lookups without a tag format

## v2.37.0 (2022-10-28)

### Feat

- add major-version-zero option to support initial package development

## v2.36.0 (2022-10-28)

### Feat

- **scripts**: remove `venv/bin/`
- **scripts**: add error message to `test`

### Fix

- **scripts/test**: MinGW64 workaround
- **scripts/test**: use double-quotes
- **scripts**: pydocstyle and cz
- **bump.py**: use `sys.stdin.isatty()`
- **scripts**: use cross-platform POSIX
- **scripts**: use portable shebang
- **pythonpackage.yml**: undo indent reformatting
- **pythonpackage.yml**: use `bash`

## v2.35.0 (2022-09-23)

### Feat

- allow fixup! and squash! in commit messages

## v2.34.0 (2022-09-19)

### Feat

- **bump**: support optional manual version argument

### Fix

- **bump**: fix type hint
- **bump**: fix typos

## v2.33.1 (2022-09-16)

### Fix

- **bump.py**: `CHANGELOG.md` gets git added and committed correctly

## v2.33.0 (2022-09-15)

### Feat

- add functionality for dev-releases

## v2.32.7 (2022-09-14)

### Fix

- **README.md**: fix pre-commit install command

## v2.32.6 (2022-09-14)

### Fix

- **bump**: log git commit stderr and stdout during bump

## v2.32.5 (2022-09-10)

### Fix

- **command_changelog**: Fixed issue #561 cz bump could not find the latest version tag with custom tag_format

## v2.32.4 (2022-09-08)

### Refactor

- **bump**: Remove a redundant join call

## v2.32.3 (2022-09-07)

### Fix

- **bump**: Search for version number line by line

## v2.32.2 (2022-08-22)

### Fix

- **bump**: Support regexes containing colons

## v2.32.1 (2022-08-21)

### Fix

- **git**: Improves error checking in get_tags
- **git**: improves git error checking in get_commits

### Refactor

- **git**: test the git log parser behaves properly when the repository has no commits
- **changelog**: fixes logic issue made evident by latest fix(git) commit

## v2.32.0 (2022-08-21)

### Feat

- **pre-commit**: Add commitizen-branch hook

## v2.31.0 (2022-08-14)

### Fix

- **pyproject.toml**: remove test added configurations
- **changelog**: use defaults.change_type_order in conventional commit
- capitalize types in default change_type_order

### Feat

- new file

## v2.30.0 (2022-08-14)

### Feat

- Determine newline to write with Git

## v2.29.6 (2022-08-13)

### Fix

- **cmd**: improve character encoding detection for sub-commands

## v2.29.5 (2022-08-07)

### Fix

- **git**: use "git tag -v" return_code to check whether a tag is signed

## v2.29.4 (2022-08-05)

### Refactor

- **tool**: use charset_normalizer instead of chardet

## v2.29.3 (2022-08-02)

### Refactor

- **changelog**: removes unused code. duplicates are found in changelog_parser

## v2.29.2 (2022-07-27)

### Fix

- **bump**: send changelog to stdout when `dry-run` is paired with `changelog-to-stdout`

## v2.29.1 (2022-07-26)

### Fix

- **Check**: process empty commit message
- **ConventionalCommitsCz**: cz's schema validates the whole commit message now

### Refactor

- **Check**: remove the extra preprocessing of commit message file

## v2.29.0 (2022-07-22)

### Feat

- use chardet to get correct encoding
- **bump**: add signed tag support for bump command

### Fix

- avoid that pytest overrides existing gpg config
- **test**: set git to work with gpg

## v2.28.1 (2022-07-22)

### Fix

- **changelog**: skip non-compliant commit subjects when building changelog

## v2.28.0 (2022-07-03)

### Feat

- **bump**: make increment option case insensitive

## v2.27.1 (2022-05-22)

### Fix

- **pre-commit**: Use new --allow-abort option
- **pre-commit**: Confine hook to commit-msg stage
- **pre-commit**: Set min pre-commit to v1.4.3
- **pre-commit**: Don't require serial execution

## v2.27.0 (2022-05-16)

### Feat

- **bump**: let it respect pre-commit reformats when bumping

## v2.26.0 (2022-05-14)

### Feat

- **check**: Add --allow-abort option

## v2.25.0 (2022-05-10)

### Feat

- **changelog**: Improve whitespace in changelog

### Refactor

- **changelog**: Simplify incremental_build

## v2.24.0 (2022-04-15)

### Fix

- change error code for NoneIncrementExit

### Feat

- add --no-raise to avoid raising error codes

## v2.23.0 (2022-03-29)

### Feat

- **customize.py**: adding support for commit_parser, changelog_pattern, change_type_map

## v2.22.0 (2022-03-29)

### Refactor

- speed up testing and wait for tags
- **git**: use date as a function in GitTag to easily patch

### Feat

- **changelog**: add support for single version and version range

## v2.21.2 (2022-02-22)

### Fix

- remove type ignore

## v2.21.1 (2022-02-22)

### Refactor

- Switch to issue forms
- Switch to issue forms
- Switch to issue forms

## v2.21.0 (2022-02-17)

### Feat

- skip merge messages that start with Pull request
- skip merge messages that start with Pull request

## v2.20.5 (2022-02-07)

### Refactor

- iter_modules only accepts str

### Fix

- Ignore packages that are not plugins
- Ignore packages that are not plugins

## v2.20.4 (2022-01-17)

### Fix

- **bump**: raise non zero error code when there's no eligible commit to bump
- **bump**: raise non zero error code when there's no eligible commit to bump

## v2.20.3 (2021-12-20)

### Fix

- **check**: filter out comment messege when checking

## v2.20.2 (2021-12-14)

### Fix

- **poetry**: add typing-exteions to dev

## v2.20.1 (2021-12-14)

### Refactor

- **conventional_commits**: remove duplicate patterns and import from defaults
- **config**: add CzSettings and Questions TypedDict
- **defaults**: add Settings typeddict
- **defaults**: move bump_map, bump_pattern, commit_parser from defaults to ConventionalCommitsCz

### Fix

- import TypedDict from type_extensions for backward compatibility

## v2.20.0 (2021-10-06)

### Feat

- **cli.py**: add shortcut for signoff command
- add signoff parameter to commit command

## v2.19.0 (2021-09-27)

### Feat

- utility for showing system information

## v2.18.2 (2021-09-27)

### Fix

- **cli**: handle argparse different behavior after python 3.9

## v2.18.1 (2021-09-12)

### Fix

- **commit**: correct the stage checker before committing

## v2.18.0 (2021-08-13)

### Refactor

- **shortcuts**: move check for shortcut config setting to apply to any list select

### Feat

- **prompt**: add keyboard shortcuts with config option

## v2.17.13 (2021-07-14)

## v2.17.12 (2021-07-06)

### Fix

- **git.py**: ensure signed commits in changelog when git config log.showsignature=true

## v2.17.11 (2021-06-24)

### Fix

- correct indentation for json config for better readability

## v2.17.10 (2021-06-22)

### Fix

- add support for jinja2 v3

## v2.17.9 (2021-06-11)

### Fix

- **changelog**: generating changelog after a pre-release

## v2.17.8 (2021-05-28)

### Fix

- **changelog**: annotated tags not generating proper changelog

## v2.17.7 (2021-05-26)

### Fix

- **bump**: fix error due to bumping version file without eol through regex
- **bump**: fix offset error due to partially match

## v2.17.6 (2021-05-06)

### Fix

- **cz/conventional_commits**: optionally expect '!' right before ':' in schema_pattern

## v2.17.5 (2021-05-06)

## v2.17.4 (2021-04-22)

### Fix

- version update in a docker-compose.yaml file

## v2.17.3 (2021-04-19)

### Fix

- fix multiple versions bumps when version changes the string size

## v2.17.2 (2021-04-10)

### Fix

- **bump**: replace all occurrences that match regex
- **wip**: add test for current breaking change

## v2.17.1 (2021-04-08)

### Fix

- **commands/init**: fix toml config format error

## v2.17.0 (2021-04-02)

### Feat

- Support versions on random positions

## v2.16.0 (2021-03-08)

### Feat

- **bump**: send incremental changelog to stdout and bump output to stderr

## v2.15.3 (2021-02-26)

### Fix

- add utf-8 encode when write toml file

## v2.15.2 (2021-02-24)

### Fix

- **git**: fix get_commits deliminator

## v2.15.1 (2021-02-21)

### Fix

- **config**: change read mode from `r` to `rb`

## v2.15.0 (2021-02-21)

### Feat

- **changelog**: add support for multiline BREAKING paragraph

## v2.14.2 (2021-02-06)

### Fix

- **git**: handle the empty commit and empty email cases

## v2.14.1 (2021-02-02)

### Fix

- remove yaml warnings when using '.cz.yaml'

## v2.14.0 (2021-01-20)

### Feat

- **#271**: enable creation of annotated tags when bumping

## v2.13.0 (2021-01-01)

### Refactor

- raise an InvalidConfigurationError
- **#323**: address PR feedback
- move expected COMMITS_TREE to global

### Feat

- **#319**: add optional change_type_order

## v2.12.1 (2020-12-30)

### Fix

- read commit_msg_file with utf-8

## v2.12.0 (2020-12-30)

### Feat

- **deps**: Update and relax tomlkit version requirement

## v2.11.1 (2020-12-16)

### Fix

- **commit**: attach user info to backup for permission denied issue

## v2.11.0 (2020-12-10)

### Feat

- add yaml as a config option

### feat

- **config**: add support for the new class YAMLConfig at the root of the confi internal package

## v2.10.0 (2020-12-02)

### Feat

- **commitizen/cli**: add the integration with argcomplete

## v2.9.0 (2020-12-02)

### Fix

- **json_config**: fix the emtpy_config_content method

### Feat

- **Init**: add the json config support as an option at Init
- **commitizen/config/json_config**: add json support for configuration

## v2.8.2 (2020-11-21)

### Fix

- support `!` in cz check command

## v2.8.1 (2020-11-21)

### Fix

- prevent prerelase from creating a bump when there are no commits

## v2.8.0 (2020-11-15)

### Feat

- allow files-only to set config version and create changelog

## v2.7.0 (2020-11-14)

### Feat

- **bump**: add flag `--local-version` that supports bumping only the local version instead of the public

## v2.6.0 (2020-11-04)

### Feat

- **commands/bump**: add config option to create changelog on bump

## v2.5.0 (2020-11-04)

### Feat

- **commands/changelog**: add config file options for start_rev and incremental

## v2.4.2 (2020-10-26)

### Fix

- **init.py**: mypy error (types)
- **commands/bump**: Add NoneIncrementExit to fix git fatal error when creating existing tag

### Refactor

- **commands/bump**: Remove comment and changed ... for pass

## v2.4.1 (2020-10-04)

### Fix

- **cz_customize**: make schema_pattern customiziable through config for cz_customize

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
- Use "cz version" instead
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
- **commands/commit**: use return_code to raise commit error, not stderr

### Refactor

- **cmd**: add return code to Command

## v1.23.2 (2020-07-25)

### Fix

- **bump**: add changelog file into stage when running `cz bump --changelog`

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
- **cli**: do not show traceback if the raised exception is CommitizenException
- introduce DryRunExit, ExpectedExit, NoCommandFoundError, InvalidCommandArgumentError
- use custom exception for error handling
- **error_codes**: remove unused NO_COMMIT_MSG error code

### Feat

- **cli**: enable displaying all traceback for CommitizenException when --debug flag is used

## v1.22.3 (2020-06-10)

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
- **commands/changelog**: add --start-rev argument to `cz changelog`
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
- **git**: Change get_commits into returning commits instead of lines of messages

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
- **config/ini_config**: replace outdated _parse_ini_settings with _parse_settings

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
- **cz/customize**: make jinja2 a custom requirement. if not installed use string.Template instead
- **cz/utils**: rename filters as utils
- **cli**: add back --version and remove subcommand required constraint

### Fix

- commit dry-run doesn't require staging to be clean
- correct typo to spell "convention"
- removing folder in windows throwing a PermissionError
- **scripts**: add back the delete poetry prefix
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
- first semantic version bump implementation

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

- **conventionalCommit**: moved filters to questions instead of message

### Fix

- **manifest**: included missing files

## v0.9.5 (2018-08-24)

### Fix

- **config**: home path for python versions between 3.0 and 3.5

## v0.9.4 (2018-08-02)

### Feat

- **cli**: added version

## v0.9.3 (2018-07-28)

### Feat

- **committer**: conventional commit is a bit more intelligent now

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
