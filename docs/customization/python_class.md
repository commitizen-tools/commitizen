# Customizing through a python class

The basic steps are:

1. Inheriting from `BaseCommitizen`.
2. Give a name to your rules.
3. Create a Python package using proper [build backend](https://packaging.python.org/en/latest/glossary/#term-Build-Backend)
4. Expose the class as a `commitizen.plugin` entrypoint.

Check an [example][convcomms] on how to configure `BaseCommitizen`.

You can also automate the steps above through [cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.0/).

```sh
cookiecutter gh:commitizen-tools/commitizen_cz_template
```

See [commitizen_cz_template](https://github.com/commitizen-tools/commitizen_cz_template) for details.

See [Third-party plugins](../third-party-plugins/about.md) for more details on how to create a third-party Commitizen plugin.

## Custom commit rules

Create a Python module, for example `cz_jira.py`.

Inherit from `BaseCommitizen`, and you must define `questions` and `message`. The others are optional.

```python title="cz_jira.py"
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
        return f"answers['title'] (#answers['issue'])"

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

```python title="setup.py"
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

And that's it. You can install it without uploading to PyPI by simply
doing `pip install .`

## Custom bump rules

You need to define 2 parameters inside your custom `BaseCommitizen`.

| Parameter      | Type   | Default | Description                                                                                           |
| -------------- | ------ | ------- | ----------------------------------------------------------------------------------------------------- |
| `bump_pattern` | `str`  | `None`  | Regex to extract information from commit (subject and body)                                           |
| `bump_map`     | `dict` | `None`  | Dictionary mapping the extracted information to a `SemVer` increment type (`MAJOR`, `MINOR`, `PATCH`) |

Let's see an example.

```python title="cz_strange.py"
from commitizen.cz.base import BaseCommitizen


class StrangeCommitizen(BaseCommitizen):
    bump_pattern = r"^(break|new|fix|hotfix)"
    bump_map = {"break": "MAJOR", "new": "MINOR", "fix": "PATCH", "hotfix": "PATCH"}
```

That's it, your Commitizen now supports custom rules, and you can run.

```bash
cz -n cz_strange bump
```

[convcomms]: https://github.com/commitizen-tools/commitizen/blob/master/commitizen/cz/conventional_commits/conventional_commits.py

### Custom commit validation and error message

The commit message validation can be customized by overriding the `validate_commit_message` and `format_error_message`
methods from `BaseCommitizen`. This allows for a more detailed feedback to the user where the error originates from.

```python
import re
from commitizen.cz.base import BaseCommitizen, ValidationResult
from commitizen import git


class CustomValidationCz(BaseCommitizen):
    def validate_commit_message(
        self,
        *,
        commit_msg: str,
        pattern: str | None,
        allow_abort: bool,
        allowed_prefixes: list[str],
        max_msg_length: int,
    ) -> ValidationResult:
        """Validate commit message against the pattern."""
        if not commit_msg:
            return allow_abort, [] if allow_abort else [f"commit message is empty"]
        if pattern is None:
            return True, []
        if any(map(commit_msg.startswith, allowed_prefixes)):
            return True, []
        if max_msg_length:
            msg_len = len(commit_msg.partition("\n")[0].strip())
            if msg_len > max_msg_length:
                return False, [
                    f"commit message is too long. Max length is {max_msg_length}"
                ]
        pattern_match = re.match(pattern, commit_msg)
        if pattern_match:
            return True, []
        else:
            # Perform additional validation of the commit message format
            # and add custom error messages as needed
            return False, ["commit message does not match the pattern"]

    def format_exception_message(
        self, ill_formatted_commits: list[tuple[git.GitCommit, list]]
    ) -> str:
        """Format commit errors."""
        displayed_msgs_content = "\n".join(
            (
                f'commit "{commit.rev}": "{commit.message}"'
                f"errors:\n"
                "\n".join((f"- {error}" for error in errors))
            )
            for commit, errors in ill_formatted_commits
        )
        return (
            "commit validation: failed!\n"
            "please enter a commit message in the commitizen format.\n"
            f"{displayed_msgs_content}\n"
            f"pattern: {self.schema_pattern()}"
        )
```

## Custom changelog generator

The changelog generator should just work in a very basic manner without touching anything.
You can customize it of course, and the following variables are the ones you need to add to your custom `BaseCommitizen`.

| Parameter                        | Type                                                                     | Required | Description                                                                                                                                                                                                         |
| -------------------------------- | ------------------------------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit_parser`                  | `str`                                                                    | NO       | Regex which should provide the variables explained in the [changelog description][changelog-des]                                                                                                                    |
| `changelog_pattern`              | `str`                                                                    | NO       | Regex to validate the commits, this is useful to skip commits that don't meet your ruling standards like a Merge. Usually the same as bump_pattern                                                                  |
| `change_type_map`                | `dict`                                                                   | NO       | Convert the title of the change type that will appear in the changelog, if a value is not found, the original will be provided                                                                                      |
| `changelog_message_builder_hook` | `method: (dict, git.GitCommit) -> dict | list | None`                  | NO       | Customize with extra information your message output, like adding links, this function is executed per parsed commit. Each GitCommit contains the following attrs: `rev`, `title`, `body`, `author`, `author_email`. Returning a falsy value ignore the commit. |
| `changelog_hook`                 | `method: (full_changelog: str, partial_changelog: Optional[str]) -> str` | NO       | Receives the whole and partial (if used incremental) changelog. Useful to send slack messages or notify a compliance department. Must return the full_changelog                                                     |
| `changelog_release_hook` | `method: (release: dict, tag: git.GitTag) -> dict` | NO | Receives each generated changelog release and its associated tag. Useful to enrich releases before they are rendered. Must return the update release

```python title="cz_strange.py"
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

    def changelog_release_hook(self, release: dict, tag: git.GitTag) -> dict:
        release["author"] = tag.author
        return release

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

## Raise Customize Exception

If you want `commitizen` to catch your exception and print the message, you'll have to inherit `CzException`.

```python
from commitizen.cz.exception import CzException


class NoSubjectProvidedException(CzException):
    ...
```

## Migrating from legacy plugin format

Commitizen migrated to a new plugin format relying on `importlib.metadata.EntryPoint`.
Migration should be straight-forward for legacy plugins:

- Remove the `discover_this` line from your plugin module
- Expose the plugin class under as a `commitizen.plugin` entrypoint.

The name of the plugin is now determined by the name of the entrypoint.

### Example

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

and expose the class as entrypoint in your `setuptools`:

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
