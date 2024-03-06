Customizing commitizen is not hard at all.
We have two different ways to do so.

## 1. Customize in configuration file

The basic steps are:

1. Define your custom committing or bumping rules in the configuration file.
2. Declare `name = "cz_customize"` in your configuration file, or add `-n cz_customize` when running commitizen.

Example:

```toml
[tool.commitizen]
name = "cz_customize"

[tool.commitizen.customize]
message_template = "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
example = "feature: this feature enable customize through config file"
schema = "<type>: <body>"
schema_pattern = "(feature|bug fix):(\\s.*)"
bump_pattern = "^(break|new|fix|hotfix)"
bump_map = {"break" = "MAJOR", "new" = "MINOR", "fix" = "PATCH", "hotfix" = "PATCH"}
change_type_order = ["BREAKING CHANGE", "feat", "fix", "refactor", "perf"]
info_path = "cz_customize_info.txt"
info = """
This is customized info
"""
commit_parser = "^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?"
changelog_pattern = "^(feature|bug fix)?(!)?"
change_type_map = {"feature" = "Feat", "bug fix" = "Fix"}

[[tool.commitizen.customize.questions]]
type = "list"
name = "change_type"
choices = [{value = "feature", name = "feature: A new feature."}, {value = "bug fix", name = "bug fix: A bug fix."}]
# choices = ["feature", "fix"]  # short version
message = "Select the type of change you are committing"

[[tool.commitizen.customize.questions]]
type = "input"
name = "message"
message = "Body."

[[tool.commitizen.customize.questions]]
type = "confirm"
name = "show_message"
message = "Do you want to add body message in commit?"
```

The equivalent example for a json config file:

```json
{
    "commitizen": {
        "name": "cz_customize",
        "customize": {
            "message_template": "{{change_type}}:{% if show_message %} {{message}}{% endif %}",
            "example": "feature: this feature enable customize through config file",
            "schema": "<type>: <body>",
            "schema_pattern": "(feature|bug fix):(\\s.*)",
            "bump_pattern": "^(break|new|fix|hotfix)",
            "bump_map": {
                "break": "MAJOR",
                "new": "MINOR",
                "fix": "PATCH",
                "hotfix": "PATCH"
            },
            "change_type_order": ["BREAKING CHANGE", "feat", "fix", "refactor", "perf"],
            "info_path": "cz_customize_info.txt",
            "info": "This is customized info",
            "commit_parser": "^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?",
            "changelog_pattern": "^(feature|bug fix)?(!)?",
            "change_type_map": {"feature": "Feat", "bug fix": "Fix"},
            "questions": [
                {
                    "type": "list",
                    "name": "change_type",
                    "choices": [
                        {
                            "value": "feature",
                            "name": "feature: A new feature."
                        },
                        {
                            "value": "bug fix",
                            "name": "bug fix: A bug fix."
                        }
                    ],
                    "message": "Select the type of change you are committing"
                },
                {
                    "type": "input",
                    "name": "message",
                    "message": "Body."
                },
                {
                    "type": "confirm",
                    "name": "show_message",
                    "message": "Do you want to add body message in commit?"
                }
            ]
        }
    }
}
```

And the correspondent example for a yaml json file:

```yaml
commitizen:
  name: cz_customize
  customize:
    message_template: "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example: 'feature: this feature enable customize through config file'
    schema: "<type>: <body>"
    schema_pattern: "(feature|bug fix):(\\s.*)"
    bump_pattern: "^(break|new|fix|hotfix)"
    commit_parser: "^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?",
    changelog_pattern: "^(feature|bug fix)?(!)?",
    change_type_map:
      feature: Feat
      bug fix: Fix
    bump_map:
      break: MAJOR
      new: MINOR
      fix: PATCH
      hotfix: PATCH
    change_type_order: ["BREAKING CHANGE", "feat", "fix", "refactor", "perf"]
    info_path: cz_customize_info.txt
    info: This is customized info
    questions:
    - type: list
      name: change_type
      choices:
      - value: feature
        name: 'feature: A new feature.'
      - value: bug fix
        name: 'bug fix: A bug fix.'
      message: Select the type of change you are committing
    - type: input
      name: message
      message: Body.
    - type: confirm
      name: show_message
      message: Do you want to add body message in commit?
```

### Customize configuration

| Parameter           | Type   | Default | Description                                                                                                                                                                                                                      |
| ------------------- | ------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `questions`         | `Questions` | `None`  | Questions regarding the commit message. Detailed below. The type `Questions` is an alias to `Iterable[MutableMapping[str, Any]]` which is defined in `commitizen.defaults`. It expects a list of dictionaries. |
| `message_template`  | `str`  | `None`  | The template for generating message from the given answers. `message_template` should either follow [Jinja2][jinja2] formatting specification, and all the variables in this template should be defined in `name` in `questions` |
| `example`           | `str`  | `None`  | (OPTIONAL) Provide an example to help understand the style. Used by `cz example`.                                                                                                                                                |
| `schema`            | `str`  | `None`  | (OPTIONAL) Show the schema used. Used by `cz schema`.                                                                                                                                                                            |
| `schema_pattern`    | `str`  | `None`  | (OPTIONAL) The regular expression used to do commit message validation. Used by `cz check`.                                                                                                                                      |
| `info_path`         | `str`  | `None`  | (OPTIONAL) The path to the file that contains explanation of the commit rules. Used by `cz info`. If not provided `cz info`, will load `info` instead.                                                                           |
| `info`              | `str`  | `None`  | (OPTIONAL) Explanation of the commit rules. Used by `cz info`.                                                                                                                                                                   |
| `bump_map`          | `dict` | `None`  | (OPTIONAL) Dictionary mapping the extracted information to a `SemVer` increment type (`MAJOR`, `MINOR`, `PATCH`)                                                                                                                 |
| `bump_pattern`      | `str`  | `None`  | (OPTIONAL) Regex to extract information from commit (subject and body)                                                                                                                                                           |
| `change_type_order`| `str`  | `None` | (OPTIONAL) List of strings used to order the Changelog. All other types will be sorted alphabetically. Default is `["BREAKING CHANGE", "Feat", "Fix", "Refactor", "Perf"]`                                                                                             |
| `commit_parser`     | `str`  | `None`  | (OPTIONAL) Regex to extract information used in creating changelog. [See more][changelog-spec]                                                                                                                                   |
| `changelog_pattern` | `str`  | `None`  | (OPTIONAL) Regex to understand which commits to include in the changelog                                                                                                                                                         |
| `change_type_map`   | `dict` | `None`  | (OPTIONAL) Dictionary mapping the type of the commit to a changelog entry                                                                                                                                                        |

[jinja2]: https://jinja.palletsprojects.com/en/2.10.x/
[changelog-spec]: https://commitizen-tools.github.io/commitizen/changelog/

#### Detailed `questions` content

| Parameter | Type   | Default | Description                                                                                                                                                                                     |
| --------- | ------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`    | `str`  | `None`  | The type of questions. Valid type: `list`, `input` and etc. [See More][different-question-types]                                                                                                |
| `name`    | `str`  | `None`  | The key for the value answered by user. It's used in `message_template`                                                                                                                         |
| `message` | `str`  | `None`  | Detail description for the question.                                                                                                                                                            |
| `choices` | `list` | `None`  | (OPTIONAL) The choices when `type = list`. Either use a list of values or a list of dictionaries with `name` and `value` keys. Keyboard shortcuts can be defined via `key`. See examples above. |
| `default` | `Any`  | `None`  | (OPTIONAL) The default value for this question.                                                                                                                                                 |
| `filter`  | `str`  | `None`  | (Optional) Validator for user's answer. **(Work in Progress)**                                                                                                                                  |
[different-question-types]: https://github.com/tmbo/questionary#different-question-types

#### Shortcut keys

When the [`use_shortcuts`](config.md#settings) config option is enabled, commitizen can show and use keyboard shortcuts to select items from lists directly.
For example, when using the `cz_conventional_commits` commitizen template, shortcut keys are shown when selecting the commit type. Unless otherwise defined, keyboard shortcuts will be numbered automatically.
To specify keyboard shortcuts for your custom choices, provide the shortcut using the `key` parameter in dictionary form for each choice you would like to customize.

## 2. Customize through customizing a class

The basic steps are:

1. Inheriting from `BaseCommitizen`
2. Give a name to your rules.
3. Create a python package using `setup.py`, `poetry`, etc
4. Expose the class as a `commitizen.plugin` entrypoint

Check an [example](convcomms) on how to configure `BaseCommitizen`.

You can also automate the steps above through [cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.0/).

```sh
cookiecutter gh:commitizen-tools/commitizen_cz_template
```

See [commitizen_cz_template](https://github.com/commitizen-tools/commitizen_cz_template) for details.

Once you publish your rules, you can send us a PR to the [Third-party section](./third-party-commitizen.md).

### Custom commit rules

Create a Python module, for example `cz_jira.py`.

Inherit from `BaseCommitizen`, and you must define `questions` and `message`. The others are optional.

```python
from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions


class JiraCz(BaseCommitizen):
    # Questions = Iterable[MutableMapping[str, Any]]
    # It expects a list with dictionaries.
    def questions(self) -> Questions:
        """Questions regarding the commit message."""
        questions = [
            {"type": "input", "name": "title", "message": "Commit title"},
            {"type": "input", "name": "issue", "message": "Jira Issue number:"},
        ]
        return questions

    def message(self, answers: dict) -> str:
        """Generate the message with the given answers."""
        return "{0} (#{1})".format(answers["title"], answers["issue"])

    def example(self) -> str:
        """Provide an example to help understand the style (OPTIONAL)

        Used by `cz example`.
        """
        return "Problem with user (#321)"

    def schema(self) -> str:
        """Show the schema used (OPTIONAL)

        Used by `cz schema`.
        """
        return "<title> (<issue>)"

    def info(self) -> str:
        """Explanation of the commit rules. (OPTIONAL)

        Used by `cz info`.
        """
        return "We use this because is useful"
```

The next file required is `setup.py` modified from flask version.

```python
from setuptools import setup

setup(
    name="JiraCommitizen",
    version="0.1.0",
    py_modules=["cz_jira"],
    license="MIT",
    long_description="this is a long description",
    install_requires=["commitizen"],
    entry_points={"commitizen.plugin": ["cz_jira = cz_jira:JiraCz"]},
)
```

So in the end, we would have

    .
    ├── cz_jira.py
    └── setup.py

And that's it. You can install it without uploading to pypi by simply
doing `pip install .`

If you feel like it should be part of this repo, create a PR.

### Custom bump rules

You need to define 2 parameters inside your custom `BaseCommitizen`.

| Parameter      | Type   | Default | Description                                                                                           |
| -------------- | ------ | ------- | ----------------------------------------------------------------------------------------------------- |
| `bump_pattern` | `str`  | `None`  | Regex to extract information from commit (subject and body)                                           |
| `bump_map`     | `dict` | `None`  | Dictionary mapping the extracted information to a `SemVer` increment type (`MAJOR`, `MINOR`, `PATCH`) |

Let's see an example.

```python
from commitizen.cz.base import BaseCommitizen


class StrangeCommitizen(BaseCommitizen):
    bump_pattern = r"^(break|new|fix|hotfix)"
    bump_map = {"break": "MAJOR", "new": "MINOR", "fix": "PATCH", "hotfix": "PATCH"}
```

That's it, your commitizen now supports custom rules, and you can run.

```bash
cz -n cz_strange bump
```

[convcomms]: https://github.com/commitizen-tools/commitizen/blob/master/commitizen/cz/conventional_commits/conventional_commits.py

### Custom changelog generator

The changelog generator should just work in a very basic manner without touching anything.
You can customize it of course, and this are the variables you need to add to your custom `BaseCommitizen`.

| Parameter                        | Type                                                                     | Required | Description                                                                                                                                                                                                         |
| -------------------------------- | ------------------------------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit_parser`                  | `str`                                                                    | NO       | Regex which should provide the variables explained in the [changelog description][changelog-des]                                                                                                                    |
| `changelog_pattern`              | `str`                                                                    | NO       | Regex to validate the commits, this is useful to skip commits that don't meet your ruling standards like a Merge. Usually the same as bump_pattern                                                                  |
| `change_type_map`                | `dict`                                                                   | NO       | Convert the title of the change type that will appear in the changelog, if a value is not found, the original will be provided                                                                                      |
| `changelog_message_builder_hook` | `method: (dict, git.GitCommit) -> dict | list | None`                                  | NO       | Customize with extra information your message output, like adding links, this function is executed per parsed commit. Each GitCommit contains the following attrs: `rev`, `title`, `body`, `author`, `author_email`. Returning a falsy value ignore the commit. |
| `changelog_hook`                 | `method: (full_changelog: str, partial_changelog: Optional[str]) -> str` | NO       | Receives the whole and partial (if used incremental) changelog. Useful to send slack messages or notify a compliance department. Must return the full_changelog                                                     |

```python
from commitizen.cz.base import BaseCommitizen
import chat
import compliance


class StrangeCommitizen(BaseCommitizen):
    changelog_pattern = r"^(break|new|fix|hotfix)"
    commit_parser = r"^(?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?:\s(?P<message>.*)?"
    change_type_map = {
        "feat": "Features",
        "fix": "Bug Fixes",
        "refactor": "Code Refactor",
        "perf": "Performance improvements",
    }

    def changelog_message_builder_hook(
        self, parsed_message: dict, commit: git.GitCommit
    ) -> dict | list | None:
        rev = commit.rev
        m = parsed_message["message"]
        parsed_message[
            "message"
        ] = f"{m} {rev} [{commit.author}]({commit.author_email})"
        return parsed_message

    def changelog_hook(
        self, full_changelog: str, partial_changelog: Optional[str]
    ) -> str:
        """Executed at the end of the changelog generation

        full_changelog: it's the output about to being written into the file
        partial_changelog: it's the new stuff, this is useful to send slack messages or
                           similar

        Return:
            the new updated full_changelog
        """
        if partial_changelog:
            chat.room("#committers").notify(partial_changelog)
        if full_changelog:
            compliance.send(full_changelog)
        full_changelog.replace(" fix ", " **fix** ")
        return full_changelog
```

[changelog-des]: ./changelog.md#description

### Raise Customize Exception

If you want `commitizen` to catch your exception and print the message, you'll have to inherit `CzException`.

```python
from commitizen.cz.exception import CzException


class NoSubjectProvidedException(CzException):
    ...
```

### Migrating from legacy plugin format

Commitizen migrated to a new plugin format relying on `importlib.metadata.EntryPoint`.
Migration should be straight-forward for legacy plugins:

- Remove the `discover_this` line from you plugin module
- Expose the plugin class under as a `commitizen.plugin` entrypoint.

The name of the plugin is now determined by the name of the entrypoint.

#### Example

If you were having a `CzPlugin` class in a `cz_plugin.py` module like this:

```python
from commitizen.cz.base import BaseCommitizen


class PluginCz(BaseCommitizen):
    ...


discover_this = PluginCz
```

Then remove the `discover_this` line:

```python
from commitizen.cz.base import BaseCommitizen


class PluginCz(BaseCommitizen):
    ...
```

and expose the class as entrypoint in you setuptools:

```python
from setuptools import setup

setup(
    name="MyPlugin",
    version="0.1.0",
    py_modules=["cz_plugin"],
    entry_points={"commitizen.plugin": ["plugin = cz_plugin:PluginCz"]},
    ...,
)
```

Then your plugin will be available under the name `plugin`.

## Customizing the changelog template

Commitizen gives you the possibility to provide your own changelog template, by:

- providing one with your customization class
- providing one from the current working directory and setting it:
    - as [configuration][template-config]
    - as `--template` parameter to both `bump` and `changelog` commands
- either by providing a template with the same name as the default template

By default, the template used is the `CHANGELOG.md.j2` file from the commitizen repository.

### Providing a template with your customization class

There is 3 parameters available to change the template rendering from your custom `BaseCommitizen`.

| Parameter         | Type   | Default | Description                                                                                           |
| ----------------- | ------ | ------- | ----------------------------------------------------------------------------------------------------- |
| `template`        | `str`  | `None`  | Provide your own template name (default to `CHANGELOG.md.j2`)                            |
| `template_loader` | `str`  | `None`  | Override the default template loader (so you can provide template from you customization class)       |
| `template_extras` | `dict` | `None`  | Provide some extra template parameters                                                                |

Let's see an example.

```python
from commitizen.cz.base import BaseCommitizen
from jinja2 import PackageLoader


class MyPlugin(BaseCommitizen):
    template = "CHANGELOG.md.jinja"
    template_loader = PackageLoader("my_plugin", "templates")
    template_extras = {"key": "value"}
```

This snippet will:

- use `CHANGELOG.md.jinja` as template name
- search for it in the `templates` directory for `my_plugin` package
- add the `key=value` variable in the template

### Providing a template from the current working directory

Users can provides their own template from their current working directory (your project root) by:

- providing a template with the same name (`CHANGELOG.md.j2` unless overridden by your custom class)
- setting your template path as `template` configuration
- giving your template path as `--template` parameter to `bump` and `changelog` commands

!!! Note
    The path is relative to the current working directory, aka. your project root most of the time.

### Template variables

The default template use a single `tree` variable which is a list of entries (a release) with the following format:

| Name | Type | Description |
| ---- | ---- | ----------- |
| version | `str` | The release version |
| date | `datetime` | The release date |
| changes | `list[tuple[str, list[Change]]]` | The release sorted changes list in the form `(type, changes)` |

Each `Change` has the following fields:

| Name | Type | Description |
| ---- | ---- | ----------- |
| scope | `str | None` | An optional scope |
| message | `str` | The commit message body |

!!! Note
    The field values depend on the customization class and/or the settings you provide

When using another template (either provided by a plugin or by yourself), you can also pass extra template variables
by:

- defining them in your configuration with the [`extras` settings][extras-config]
- providing them on the commandline with the `--extra/-e` parameter to `bump` and `changelog` commands

[template-config]: config.md#template
[extras-config]: config.md#extras
