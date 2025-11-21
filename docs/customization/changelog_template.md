
# Customizing the changelog template

Commitizen gives you the possibility to provide your own changelog template, by:

- providing one with your customization class
- providing one from the current working directory and setting it:
  - Through the configuration file
  - as `--template` parameter to both `bump` and `changelog` commands
- either by providing a template with the same name as the default template

By default, the template used is the `CHANGELOG.md.j2` file from the Commitizen repository.

## Providing a template with your customization class

There are 3 parameters available to change the template rendering from your custom `BaseCommitizen`.

| Parameter         | Type   | Default | Description                                                                                           |
| ----------------- | ------ | ------- | ----------------------------------------------------------------------------------------------------- |
| `template`        | `str`  | `None`  | Provide your own template name (default to `CHANGELOG.md.j2`)                                         |
| `template_loader` | `str`  | `None`  | Override the default template loader (so you can provide template from your customization class)      |
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

## Providing a template from the current working directory

Users can provide their own template from their current working directory (your project root) by:

- providing a template with the same name (`CHANGELOG.md.j2` unless overridden by your custom class)
- setting your template path as `template` configuration
- giving your template path as `--template` parameter to `bump` and `changelog` commands

!!! note
    The path is relative to the current working directory, aka your project root most of the time.

## Template variables

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
| sha1 | `str` | The commit `sha1` |
| parents | `list[str]` | The parent commit(s) `sha1`(s) |
| author | `str` | The commit author name |
| author_email | `str` | The commit author email |

!!! note
    The field values depend on the customization class and/or the settings you provide

The `parents` field can be used to identify merge commits and generate a changelog based on those. Another use case
is listing commits that belong to the same pull request.

When using another template (either provided by a plugin or by yourself), you can also pass extra template variables
by:

- defining them in your configuration with the `extras` settings
- providing them on the command line with the `--extra/-e` parameter to `bump` and `changelog` commands
