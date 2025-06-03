from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile

from commitizen import cmd, out
from commitizen.exceptions import GitCommandError


class EOLType(Enum):
    """The EOL type from `git config core.eol`."""

    LF = "lf"
    CRLF = "crlf"
    NATIVE = "native"

    @classmethod
    def for_open(cls) -> str:
        c = cmd.run("git config core.eol")
        eol = c.out.strip().upper()
        return cls._char_for_open()[cls._safe_cast(eol)]

    @classmethod
    def _safe_cast(cls, eol: str) -> EOLType:
        try:
            return cls[eol]
        except KeyError:
            return cls.NATIVE

    @classmethod
    @lru_cache
    def _char_for_open(cls) -> dict[EOLType, str]:
        """Get the EOL character for `open()`."""
        return {
            cls.LF: "\n",
            cls.CRLF: "\r\n",
            cls.NATIVE: os.linesep,
        }


class GitObject:
    rev: str
    name: str
    date: str

    def __eq__(self, other: object) -> bool:
        return hasattr(other, "rev") and self.rev == other.rev

    def __hash__(self) -> int:
        return hash(self.rev)


class GitCommit(GitObject):
    def __init__(
        self,
        rev: str,
        title: str,
        body: str = "",
        author: str = "",
        author_email: str = "",
        parents: list[str] | None = None,
    ) -> None:
        self.rev = rev.strip()
        self.title = title.strip()
        self.body = body.strip()
        self.author = author.strip()
        self.author_email = author_email.strip()
        self.parents = parents or []

    @property
    def message(self) -> str:
        return f"{self.title}\n\n{self.body}".strip()

    @classmethod
    def from_rev_and_commit(cls, rev_and_commit: str) -> GitCommit:
        """Create a GitCommit instance from a formatted commit string.

        This method parses a multi-line string containing commit information in the following format:
        ```
        <rev>
        <parents>
        <title>
        <author>
        <author_email>
        <body_line_1>
        <body_line_2>
        ...
        ```

        Args:
            rev_and_commit (str): A string containing commit information with fields separated by newlines.
                - rev: The commit hash/revision
                - parents: Space-separated list of parent commit hashes
                - title: The commit title/message
                - author: The commit author's name
                - author_email: The commit author's email
                - body: Optional multi-line commit body

        Returns:
            GitCommit: A new GitCommit instance with the parsed information.

        Example:
            >>> commit_str = '''abc123
            ... def456 ghi789
            ... feat: add new feature
            ... John Doe
            ... john@example.com
            ... This is a detailed description
            ... of the new feature'''
            >>> commit = GitCommit.from_rev_and_commit(commit_str)
            >>> commit.rev
            'abc123'
            >>> commit.title
            'feat: add new feature'
            >>> commit.parents
            ['def456', 'ghi789']
        """
        rev, parents, title, author, author_email, *body_list = rev_and_commit.split(
            "\n"
        )
        return cls(
            rev=rev.strip(),
            title=title.strip(),
            body="\n".join(body_list).strip(),
            author=author,
            author_email=author_email,
            parents=[p for p in parents.strip().split(" ") if p],
        )

    def __repr__(self) -> str:
        return f"{self.title} ({self.rev})"


class GitTag(GitObject):
    def __init__(self, name: str, rev: str, date: str) -> None:
        self.rev = rev.strip()
        self.name = name.strip()
        self._date = date.strip()

    def __repr__(self) -> str:
        return f"GitTag('{self.name}', '{self.rev}', '{self.date}')"

    @property
    def date(self) -> str:
        return self._date

    @date.setter
    def date(self, value: str) -> None:
        self._date = value

    @classmethod
    def from_line(cls, line: str, inner_delimiter: str) -> GitTag:
        name, objectname, date, obj = line.split(inner_delimiter)
        if not obj:
            obj = objectname

        return cls(name=name, rev=obj, date=date)


def tag(
    tag: str, annotated: bool = False, signed: bool = False, msg: str | None = None
) -> cmd.Command:
    if not annotated and not signed:
        return cmd.run(f"git tag {tag}")

    # according to https://git-scm.com/book/en/v2/Git-Basics-Tagging,
    # we're not able to create lightweight tag with message.
    # by adding message, we make it a annotated tags
    option = "-s" if signed else "-a"  # The else case is for annotated tags
    return cmd.run(f'git tag {option} {tag} -m "{msg or tag}"')


def add(*args: str) -> cmd.Command:
    return cmd.run(f"git add {' '.join(args)}")


def commit(
    message: str,
    args: str = "",
    committer_date: str | None = None,
) -> cmd.Command:
    f = NamedTemporaryFile("wb", delete=False)
    f.write(message.encode("utf-8"))
    f.close()

    command = _create_commit_cmd_string(args, committer_date, f.name)
    c = cmd.run(command)
    os.unlink(f.name)
    return c


def _create_commit_cmd_string(args: str, committer_date: str | None, name: str) -> str:
    command = f'git commit {args} -F "{name}"'
    if not committer_date:
        return command
    if os.name != "nt":
        return f"GIT_COMMITTER_DATE={committer_date} {command}"
    # Using `cmd /v /c "{command}"` sets environment variables only for that command
    return f'cmd /v /c "set GIT_COMMITTER_DATE={committer_date}&& {command}"'


def get_commits(
    start: str | None = None,
    end: str | None = None,
    *,
    args: str = "",
) -> list[GitCommit]:
    """Get the commits between start and end."""
    if end is None:
        end = "HEAD"
    git_log_entries = _get_log_as_str_list(start, end, args)
    return [
        GitCommit.from_rev_and_commit(rev_and_commit)
        for rev_and_commit in git_log_entries
        if rev_and_commit
    ]


def get_filenames_in_commit(git_reference: str = "") -> list[str]:
    """Get the list of files that were committed in the requested git reference.

    :param git_reference: a git reference as accepted by `git show`, default: the last commit

    :returns: file names committed in the last commit by default or inside the passed git reference
    """
    c = cmd.run(f"git show --name-only --pretty=format: {git_reference}")
    if c.return_code == 0:
        return c.out.strip().split("\n")
    raise GitCommandError(c.err)


def get_tags(
    dateformat: str = "%Y-%m-%d", reachable_only: bool = False
) -> list[GitTag]:
    inner_delimiter = "---inner_delimiter---"
    formatter = (
        f'"%(refname:lstrip=2){inner_delimiter}'
        f"%(objectname){inner_delimiter}"
        f"%(creatordate:format:{dateformat}){inner_delimiter}"
        f'%(object)"'
    )
    extra = "--merged" if reachable_only else ""
    # Force the default language for parsing
    env = {"LC_ALL": "C", "LANG": "C", "LANGUAGE": "C"}
    c = cmd.run(f"git tag --format={formatter} --sort=-creatordate {extra}", env=env)
    if c.return_code != 0:
        if reachable_only and c.err == "fatal: malformed object name HEAD\n":
            # this can happen if there are no commits in the repo yet
            return []
        raise GitCommandError(c.err)

    if c.err:
        out.warn(f"Attempting to proceed after: {c.err}")

    return [
        GitTag.from_line(line=line, inner_delimiter=inner_delimiter)
        for line in c.out.split("\n")[:-1]
    ]


def tag_exist(tag: str) -> bool:
    c = cmd.run(f"git tag --list {tag}")
    return tag in c.out


def is_signed_tag(tag: str) -> bool:
    return cmd.run(f"git tag -v {tag}").return_code == 0


def get_latest_tag_name() -> str | None:
    c = cmd.run("git describe --abbrev=0 --tags")
    if c.err:
        return None
    return c.out.strip()


def get_tag_message(tag: str) -> str | None:
    c = cmd.run(f"git tag -l --format='%(contents:subject)' {tag}")
    if c.err:
        return None
    return c.out.strip()


def get_tag_names() -> list[str]:
    c = cmd.run("git tag --list")
    if c.err:
        return []
    return [tag for raw in c.out.split("\n") if (tag := raw.strip())]


def find_git_project_root() -> Path | None:
    c = cmd.run("git rev-parse --show-toplevel")
    if c.err:
        return None
    return Path(c.out.strip())


def is_staging_clean() -> bool:
    """Check if staging is clean."""
    c = cmd.run("git diff --no-ext-diff --cached --name-only")
    return not bool(c.out)


def is_git_project() -> bool:
    c = cmd.run("git rev-parse --is-inside-work-tree")
    return c.out.strip() == "true"


def get_core_editor() -> str | None:
    c = cmd.run("git var GIT_EDITOR")
    if c.out:
        return c.out.strip()
    return None


def smart_open(*args, **kwargs):  # type: ignore[no-untyped-def,unused-ignore] # noqa: ANN201
    """Open a file with the EOL style determined from Git."""
    return open(*args, newline=EOLType.for_open(), **kwargs)


def _get_log_as_str_list(start: str | None, end: str, args: str) -> list[str]:
    """Get string representation of each log entry"""
    delimiter = "----------commit-delimiter----------"
    log_format: str = "%H%n%P%n%s%n%an%n%ae%n%b"
    command_range = f"{start}..{end}" if start else end
    command = f"git -c log.showSignature=False log --pretty={log_format}{delimiter} {args} {command_range}"

    c = cmd.run(command)
    if c.return_code != 0:
        raise GitCommandError(c.err)
    return c.out.split(f"{delimiter}\n")


def get_default_branch() -> str:
    c = cmd.run("git symbolic-ref refs/remotes/origin/HEAD")
    if c.return_code != 0:
        raise GitCommandError(c.err)
    return c.out.strip()
