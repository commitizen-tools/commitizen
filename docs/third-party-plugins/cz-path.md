# [cz-path](https://pypi.org/project/cz-path/)

Provides prefix choices for commit messages based on staged files (Git only).
For example, if the staged files are `component/z/a.ts` and `component/z/b.ts`,
the path prefix option will be `component/z` and commit message might look like:
`component/z/: description of changes`. If only one file is staged, the extension
is removed in the prefix.

This plugins provides a commitizen convention for commit messages.

## Installation

```sh
pip install cz-path
```

## Usage

Add `cz-path` to your configuration file.

Example for `.cz.json`:

```json
{
  "commitizen": {
    "name": "cz_path",
    "remove_path_prefixes": ["src", "module_name"]
  }
}
```

The default value for `remove_path_prefixes` is `["src"]`. Adding `/` to the
prefixes is not required.

## Example session

```plain
 $ git add .vscode/
 $ cz -n cz_path c
? Prefix: (Use arrow keys)
 » .vscode
   .vscode/
   project
   (empty)
? Prefix: .vscode
? Commit title: adjust settings

.vscode: adjust settings

[main 0000000] .vscode: adjust settings
 2 files changed, 1 insertion(+), 11 deletions(-)

Commit successful!
```
