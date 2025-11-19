# Customize in configuration file

The basic steps are:

1. Define your custom committing or bumping rules in the configuration file.
2. Declare `name = "cz_customize"` in your configuration file, or add `-n cz_customize` when running Commitizen.

Example:

```toml title="pyproject.toml"
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

```json title=".cz.json"
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

And the correspondent example for a yaml file:

```yaml title=".cz.yaml"
commitizen:
  name: cz_customize
  customize:
    message_template: '{{change_type}}:{% if show_message %} {{message}}{% endif %}'
    example: 'feature: this feature enable customize through config file'
    schema: '<type>: <body>'
    schema_pattern: '(feature|bug fix):(\\s.*)'
    bump_pattern: '^(break|new|fix|hotfix)'
    commit_parser: '^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?'
    changelog_pattern: '^(feature|bug fix)?(!)?'
    change_type_map:
      feature: Feat
      bug fix: Fix
    bump_map:
      break: MAJOR
      new: MINOR
      fix: PATCH
      hotfix: PATCH
    change_type_order: ['BREAKING CHANGE', 'feat', 'fix', 'refactor', 'perf']
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
      message: 'Body.'
    - type: confirm
      name: show_message
      message: 'Do you want to add body message in commit?'
```

## Configuration File Options

| Parameter           | Type   | Default | Description                                                                                                                                                                                                                      |
| ------------------- | ------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `questions`         | `Questions` | `None`  | Questions regarding the commit message. Detailed below. The type `Questions` is an alias to `Iterable[MutableMapping[str, Any]]` which is defined in `commitizen.defaults`. It expects a list of dictionaries.              |
| `message_template`  | `str`  | `None`  | The template for generating message from the given answers. `message_template` should either follow [Jinja2][jinja2] formatting specification, and all the variables in this template should be defined in `name` in `questions` |
| `example`           | `str`  | `""`    | (OPTIONAL) Provide an example to help understand the style. Used by `cz example`.                                                                                                                                                |
| `schema`            | `str`  | `""`    | (OPTIONAL) Show the schema used. Used by `cz schema`.                                                                                                                                                                            |
| `schema_pattern`    | `str`  | `""`    | (OPTIONAL) The regular expression used to do commit message validation. Used by `cz check`.                                                                                                                                      |
| `info_path`         | `str`  | `""`    | (OPTIONAL) The path to the file that contains explanation of the commit rules. Used by `cz info`. If not provided `cz info`, will load `info` instead.                                                                           |
| `info`              | `str`  | `""`    | (OPTIONAL) Explanation of the commit rules. Used by `cz info`.                                                                                                                                                                   |
| `bump_map`          | `dict` | `None`  | (OPTIONAL) Dictionary mapping the extracted information to a `SemVer` increment type (`MAJOR`, `MINOR`, `PATCH`)                                                                                                                 |
| `bump_pattern`      | `str`  | `None`  | (OPTIONAL) Regex to extract information from commit (subject and body)                                                                                                                                                           |
| `change_type_order` | `str`  | `None`  | (OPTIONAL) List of strings used to order the Changelog. All other types will be sorted alphabetically. Default is `["BREAKING CHANGE", "Feat", "Fix", "Refactor", "Perf"]`                                                       |
| `commit_parser`     | `str`  | `None`  | (OPTIONAL) Regex to extract information used in creating changelog. [See more][changelog-spec]                                                                                                                                   |
| `changelog_pattern` | `str`  | `None`  | (OPTIONAL) Regex to understand which commits to include in the changelog                                                                                                                                                         |
| `change_type_map`   | `dict` | `None`  | (OPTIONAL) Dictionary mapping the type of the commit to a changelog entry                                                                                                                                                        |

[jinja2]: https://jinja.palletsprojects.com/en/2.10.x/
[changelog-spec]: https://commitizen-tools.github.io/commitizen/commands/changelog/

### Detailed `questions` content

| Parameter   | Type   | Default | Description                                                                                                                                                                                     |
| ----------- | ------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`      | `str`  | `None`  | The type of questions. Valid types: `list`, `select`, `input`, etc. The `select` type provides an interactive searchable list interface. [See More][different-question-types]                  |
| `name`      | `str`  | `None`  | The key for the value answered by user. It's used in `message_template`                                                                                                                         |
| `message`   | `str`  | `None`  | Detail description for the question.                                                                                                                                                            |
| `choices`   | `list` | `None`  | (OPTIONAL) The choices when `type = list` or `type = select`. Either use a list of values or a list of dictionaries with `name` and `value` keys. Keyboard shortcuts can be defined via `key`. See examples above. |
| `default`   | `Any`  | `None`  | (OPTIONAL) The default value for this question.                                                                                                                                                 |
| `filter`    | `str`  | `None`  | (OPTIONAL) Validator for user's answer. **(Work in Progress)**                                                                                                                                  |
| `multiline` | `bool` | `False` | (OPTIONAL) Enable multiline support when `type = input`.                                                                                                                                        |
| `use_search_filter` | `bool` | `False` | (OPTIONAL) Enable search/filter functionality for list/select type questions. This allows users to type and filter through the choices.                                                  |
| `use_jk_keys` | `bool` | `True` | (OPTIONAL) Enable/disable j/k keys for navigation in list/select type questions. Set to false if you prefer arrow keys only.                                                                    |

[different-question-types]: https://github.com/tmbo/questionary#different-question-types

### Shortcut keys

When the `use_shortcuts` config option is enabled, Commitizen can show and use keyboard shortcuts to select items from lists directly.
For example, when using the `cz_conventional_commits` Commitizen template, shortcut keys are shown when selecting the commit type.
Unless otherwise defined, keyboard shortcuts will be numbered automatically.
To specify keyboard shortcuts for your custom choices, provide the shortcut using the `key` parameter in dictionary form for each choice you would like to customize.
