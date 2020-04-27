## About

This command will generate a changelog following the commiting rules established.

## Usage

In the command line run

```bash
cz changelog
```

```bash
cz ch
```

It has support for incremental changelog:

- Build from latest version found in changelog, this is useful if you have a different changelog and want to use chommitizen
- Update unreleased area
- Allows users to manually touch the changelog without being rewritten.

## Constrains

At the moment this features is constrained only to markdown files.

## Description

These are the variables used by the changelog generator.

```md
# <version> (<date>)

## <change_type>

- **<scope>**: <message>
```

It will create a full block like above per version found in the tags.
And it will create a list of the commits found.
The `change_type` and the `scope` are optional, they don't need to be provided,
but if your regex does they will be rendered.

The format followed by the changelog is the one from [keep a changelog][keepachangelog]
and the following variables are expected:

| Variable      | Description                                                                                    | Source         |
| ------------- | ---------------------------------------------------------------------------------------------- | -------------- |
| `version`     | Version number which should follow [semver][semver]                                            | `tags`         |
| `date`        | Date in which the tag was created                                                              | `tags`         |
| `change_type` | The group where the commit belongs to, this is optional. Example: fix                          | `commit regex` |
| `message`\*   | Information extracted from the commit message                                                  | `commit regex` |
| `scope`       | Contextual information. Should be parsed using the regex from the message, it will be **bold** | `commit regex` |
| `breaking`    | Wether is a breaking change or not                                                             | `commit regex` |

- **required**: is the only one required to be parsed by the regex

## TODO

- [ ] support for hooks: this would allow introduction of custom information in the commiter, like a github or jira url. Eventually we could build a `CzConventionalGithub`, which would add links to commits
- [ ] support for map: allow the usage of a `change_type` mapper, to convert from feat to feature for example.

[keepachangelog]: https://keepachangelog.com/
[semver]: https://semver.org/
