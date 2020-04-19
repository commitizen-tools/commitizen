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

## Description

These are the variables used by the changelog generator.

```md
# <version> (<date>)

## <change_type>

- **<scope>**: <message>
```

It will create a full of the above block per version found in the tags.
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

[keepachangelog]: https://keepachangelog.com/
[semver]: https://semver.org/
