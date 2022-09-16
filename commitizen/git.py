import os
from enum import Enum
from os import linesep
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional

from commitizen import cmd, out
from commitizen.exceptions import GitCommandError

UNIX_EOL = "\n"
WINDOWS_EOL = "\r\n"


class EOLTypes(Enum):
    """The EOL type from `git config core.eol`."""

    LF = "lf"
    CRLF = "crlf"
    NATIVE = "native"

    def get_eol_for_open(self) -> str:
        """Get the EOL character for `open()`."""
        map = {
            EOLTypes.CRLF: WINDOWS_EOL,
            EOLTypes.LF: UNIX_EOL,
            EOLTypes.NATIVE: linesep,
        }

        return map[self]


class GitObject:
    rev: str
    name: str
    date: str

    def __eq__(self, other) -> bool:
        if not hasattr(other, "rev"):
            return False
        return self.rev == other.rev  # type: ignore


class GitCommit(GitObject):
    def __init__(
        self, rev, title, body: str = "", author: str = "", author_email: str = ""
    ):
        self.rev = rev.strip()
        self.title = title.strip()
        self.body = body.strip()
        self.author = author.strip()
        self.author_email = author_email.strip()

    @property
    def message(self):
        return f"{self.title}\n\n{self.body}".strip()

    def __repr__(self):
        return f"{self.title} ({self.rev})"


class GitTag(GitObject):
    def __init__(self, name, rev, date):
        self.rev = rev.strip()
        self.name = name.strip()
        self._date = date.strip()

    def __repr__(self):
        return f"GitTag('{self.name}', '{self.rev}', '{self.date}')"

    @property
    def date(self):
        return self._date

    @classmethod
    def from_line(cls, line: str, inner_delimiter: str) -> "GitTag":

        name, objectname, date, obj = line.split(inner_delimiter)
        if not obj:
            obj = objectname

        return cls(name=name, rev=obj, date=date)


def tag(tag: str, annotated: bool = False, signed: bool = False) -> cmd.Command:
    _opt = ""
    if annotated:
        _opt = f"-a {tag} -m"
    if signed:
        _opt = f"-s {tag} -m"
    c = cmd.run(f"git tag {_opt} {tag}")
    return c


def commit(message: str, args: str = "") -> cmd.Command:
    f = NamedTemporaryFile("wb", delete=False)
    f.write(message.encode("utf-8"))
    f.close()
    c = cmd.run(f"git commit {args} -F {f.name}")
    os.unlink(f.name)
    return c


def get_commits(
    start: Optional[str] = None,
    end: str = "HEAD",
    *,
    args: str = "",
) -> List[GitCommit]:
    """Get the commits between start and end."""
    git_log_entries = _get_log_as_str_list(start, end, args)
    git_commits = []
    for rev_and_commit in git_log_entries:
        if not rev_and_commit:
            continue
        rev, title, author, author_email, *body_list = rev_and_commit.split("\n")
        if rev_and_commit:
            git_commit = GitCommit(
                rev=rev.strip(),
                title=title.strip(),
                body="\n".join(body_list).strip(),
                author=author,
                author_email=author_email,
            )
            git_commits.append(git_commit)
    return git_commits


def get_filenames_in_commit(git_reference: str = ""):
    """Get the list of files that were committed in the requested git reference.

    :param git_reference: a git reference as accepted by `git show`, default: the last commit

    :returns: file names committed in the last commit by default or inside the passed git reference
    """
    c = cmd.run(f"git show --name-only --pretty=format: {git_reference}")
    if c.return_code == 0:
        return c.out.strip().split("\n")
    else:
        raise GitCommandError(c.err)


def get_tags(dateformat: str = "%Y-%m-%d") -> List[GitTag]:
    inner_delimiter = "---inner_delimiter---"
    formatter = (
        f'"%(refname:lstrip=2){inner_delimiter}'
        f"%(objectname){inner_delimiter}"
        f"%(creatordate:format:{dateformat}){inner_delimiter}"
        f'%(object)"'
    )
    c = cmd.run(f"git tag --format={formatter} --sort=-creatordate")
    if c.return_code != 0:
        raise GitCommandError(c.err)

    if c.err:
        out.warn(f"Attempting to proceed after: {c.err}")

    if not c.out:
        return []

    git_tags = [
        GitTag.from_line(line=line, inner_delimiter=inner_delimiter)
        for line in c.out.split("\n")[:-1]
    ]

    return git_tags


def tag_exist(tag: str) -> bool:
    c = cmd.run(f"git tag --list {tag}")
    return tag in c.out


def is_signed_tag(tag: str) -> bool:
    return cmd.run(f"git tag -v {tag}").return_code == 0


def get_latest_tag_name() -> Optional[str]:
    c = cmd.run("git describe --abbrev=0 --tags")
    if c.err:
        return None
    return c.out.strip()


def get_tag_names() -> List[Optional[str]]:
    c = cmd.run("git tag --list")
    if c.err:
        return []
    return [tag.strip() for tag in c.out.split("\n") if tag.strip()]


def find_git_project_root() -> Optional[Path]:
    c = cmd.run("git rev-parse --show-toplevel")
    if not c.err:
        return Path(c.out.strip())
    return None


def is_staging_clean() -> bool:
    """Check if staging is clean."""
    c = cmd.run("git diff --no-ext-diff --cached --name-only")
    return not bool(c.out)


def is_git_project() -> bool:
    c = cmd.run("git rev-parse --is-inside-work-tree")
    if c.out.strip() == "true":
        return True
    return False


def get_eol_style() -> EOLTypes:
    c = cmd.run("git config core.eol")
    eol = c.out.strip().lower()

    # We enumerate the EOL types of the response of
    # `git config core.eol`, and map it to our enumration EOLTypes.
    #
    # It is just like the varient of the "match" syntax.
    map = {
        "lf": EOLTypes.LF,
        "crlf": EOLTypes.CRLF,
        "native": EOLTypes.NATIVE,
    }

    # If the response of `git config core.eol` is in the map:
    if eol in map:
        return map[eol]
    else:
        # The default value is "native".
        # https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreeol
        return map["native"]


def smart_open(*args, **kargs):
    """Open a file with the EOL style determined from Git."""
    return open(*args, newline=get_eol_style().get_eol_for_open(), **kargs)


def _get_log_as_str_list(start: Optional[str], end: str, args: str) -> List[str]:
    """Get string representation of each log entry"""
    delimiter = "----------commit-delimiter----------"
    log_format: str = "%H%n%s%n%an%n%ae%n%b"
    git_log_cmd = (
        f"git -c log.showSignature=False log --pretty={log_format}{delimiter} {args}"
    )
    if start:
        command = f"{git_log_cmd} {start}..{end}"
    else:
        command = f"{git_log_cmd} {end}"
    c = cmd.run(command)
    if c.return_code != 0:
        raise GitCommandError(c.err)
    if not c.out:
        return []
    return c.out.split(f"{delimiter}\n")
