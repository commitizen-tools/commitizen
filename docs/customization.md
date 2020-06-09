Customizing commitizen is not hard at all.

## Customize through customizing a class

The basic steps are:

1. Inheriting from `BaseCommitizen`
2. Give a name to your rules.
3. Expose the class at the end of your file assigning it to `discover_this`
4. Create a python package starting with `cz_` using `setup.py`, `poetry`, etc

Check an [example](convcomms) on how to configure `BaseCommitizen`.

You can also automate the steps above through [cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.0/).

```sh
cookiecutter gh:commitizen-tools/commitizen_cz_template
```

See [commitizen_cz_template](https://github.com/commitizen-tools/commitizen_cz_template) for detail.

### Custom commit rules

Create a file starting with `cz_`, for example `cz_jira.py`. This prefix is used to detect the plug-in. Same method [flask uses]

Inherit from `BaseCommitizen`, and you must define `questions` and
`message`. The others are optional.

```python
from commitizen.cz.base import BaseCommitizen

class JiraCz(BaseCommitizen):

    def questions(self) -> list:
        """Questions regarding the commit message."""
        questions = [
            {
                'type': 'input',
                'name': 'title',
                'message': 'Commit title'
            },
            {
                'type': 'input',
                'name': 'issue',
                'message': 'Jira Issue number:'
            },
        ]
        return questions

    def message(self, answers: dict) -> str:
        """Generate the message with the given answers."""
        return '{0} (#{1})'.format(answers['title'], answers['issue'])

    def example(self) -> str:
        """Provide an example to help understand the style (OPTIONAL)

        Used by `cz example`.
        """
        return 'Problem with user (#321)'

    def schema(self) -> str:
        """Show the schema used (OPTIONAL)

        Used by `cz schema`.
        """
        return '<title> (<issue>)'

    def info(self) -> str:
        """Explanation of the commit rules. (OPTIONAL)

        Used by `cz info`.
        """
        return 'We use this because is useful'


discover_this = JiraCz  # used by the plug-in system
```

The next file required is `setup.py` modified from flask version.

```python
from setuptools import setup

setup(
    name='JiraCommitizen',
    version='0.1.0',
    py_modules=['cz_jira'],
    license='MIT',
    long_description='this is a long description',
    install_requires=['commitizen']
)
```

So in the end, we would have

    .
    ├── cz_jira.py
    └── setup.py

And that's it. You can install it without uploading to pypi by simply
doing `pip install .`

If you feel like it should be part of this repo, create a PR.

[flask uses]: http://flask.pocoo.org/docs/0.12/extensiondev/

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

## Custom changelog generator

The changelog generator should just work in a very basic manner without touching anything.
You can customize it of course, and this are the variables you need to add to your custom `BaseCommitizen`.

| Parameter           | Type                                                                     | Required | Description                                                                                                                                                     |
| ------------------- | ------------------------------------------------------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit_parser`     | `str`                                                                    | NO       | Regex which should provide the variables explained in the [changelog description][changelog-des]                                                                |
| `changelog_pattern` | `str`                                                                    | NO       | Regex to validate the commits, this is useful to skip commits that don't meet your rulling standards like a Merge. Usually the same as bump_pattern             |
| `change_type_map`   | `dict`                                                                   | NO       | Convert the title of the change type that will appear in the changelog, if a value is not found, the original will be provided                                  |
| `changelog_message_builder_hook`      | `method: (dict, git.GitCommit) -> dict`                                  | NO       | Customize with extra information your message output, like adding links, this function is executed per parsed commit.                                           |
| `changelog_hook`    | `method: (full_changelog: str, partial_changelog: Optional[str]) -> str` | NO       | Receives the whole and partial (if used incremental) changelog. Useful to send slack messages or notify a compliance department. Must return the full_changelog |

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
        "perf": "Performance improvements"
    }

    def changelog_message_builder_hook(self, parsed_message: dict, commit: git.GitCommit) -> dict:
        rev = commit.rev
        m = parsed_message["message"]
        parsed_message["message"] = f"{m} {rev}"
        return parsed_message

    def changelog_hook(self, full_changelog: str, partial_changelog: Optional[str]) -> str:
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
        full_changelog.replace(' fix ', ' **fix** ')
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

## Customize in toml

**This is only supported when configuring through `toml` (e.g., `pyproject.toml`, `.cz`, and `.cz.toml`)**

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
bump_pattern = "^(break|new|fix|hotfix)"
bump_map = {"break" = "MAJOR", "new" = "MINOR", "fix" = "PATCH", "hotfix" = "PATCH"}
info_path = "cz_customize_info.txt"
info = """
This is customized info
"""

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

### Customize configuration

| Parameter          | Type   | Default | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------ | ------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `questions`         | `dict` | `None`  | Questions regarding the commit message. Detailed below.                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `message_template` | `str`  | `None`  | The template for generating message from the given answers. `message_template` should either follow the [string.Template](https://docs.python.org/3/library/string.html#template-strings) or [Jinja2](https://jinja.palletsprojects.com/en/2.10.x/) formatting specification, and all the variables in this template should be defined in `name` in `questions`. Note that `Jinja2` is not installed by default. If not installed, commitizen will use `string.Template` formatting. |
| `example`          | `str`  | `None`  | (OPTIONAL) Provide an example to help understand the style. Used by `cz example`.                                                                                                                                                                                                                                                                                                                                                                                                    |
| `schema`           | `str`  | `None`  | (OPTIONAL) Show the schema used. Used by `cz schema`.                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `info_path`        | `str`  | `None`  | (OPTIONAL) The path to the file that contains explanation of the commit rules. Used by `cz info`. If not provided `cz info`, will load `info` instead.                                                                                                                                                                                                                                                                                                                               |
| `info`             | `str`  | `None`  | (OPTIONAL) Explanation of the commit rules. Used by `cz info`.                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `bump_map`         | `dict` | `None`  | (OPTIONAL) Dictionary mapping the extracted information to a `SemVer` increment type (`MAJOR`, `MINOR`, `PATCH`)                                                                                                                                                                                                                                                                                                                                                                     |
| `bump_pattern`     | `str`  | `None`  | (OPTIONAL) Regex to extract information from commit (subject and body)                                                                                                                                                                                                                                                                                                                                                                                                               |

#### Detailed `questions` content

| Parameter | Type   | Default | Description                                                                                                                                                                                                                  |
| --------- | ------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`    | `str`  | `None`  | The type of questions. Valid type: `list`, `input` and etc. [See More](https://github.com/tmbo/questionary#different-question-types)                                                                                         |
| `name`    | `str`  | `None`  | The key for the value answered by user. It's used in `message_template`                                                                                                                                                      |
| `message` | `str`  | `None`  | Detail description for the question.                                                                                                                                                                                         |
| `choices` | `list` | `None`  | (OPTIONAL) The choices when `type = list`. Either use a list of values or a list of dicitionaries with `name` and `value` keys. See examples above. |
| `default` | `Any`  | `None`  | (OPTIONAL) The default value for this question.                                                                                                                                                                              |
| `filter`  | `str`  | `None`  | (Optional) Validator for user's answer. **(Work in Progress)**                                                                                                                                                               |
