import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional

from commitizen import cmd


class GitObject:
    rev: str
    name: str
    date: str

    def __eq__(self, other) -> bool:
        if not hasattr(other, "rev"):
            return False
        return self.rev == other.rev


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
        self.date = date.strip()

    def __repr__(self):
        return f"GitTag('{self.name}', '{self.rev}', '{self.date}')"


def tag(tag: str, annotated: bool = False):
    c = cmd.run(f"git tag -a {tag} -m {tag}" if annotated else f"git tag {tag}")
    return c


def commit(message: str, args: str = ""):
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
    log_format: str = "%H%n%s%n%an%n%ae%n%b",
    delimiter: str = "----------commit-delimiter----------",
    args: str = "",
) -> List[GitCommit]:
    """Get the commits between start and end."""
    git_log_cmd = f"git log --pretty={log_format}{delimiter} {args}"

    if start:
        c = cmd.run(f"{git_log_cmd} {start}..{end}")
    else:
        c = cmd.run(f"{git_log_cmd} {end}")

    if not c.out:
        return []

    git_commits = []
    for rev_and_commit in c.out.split(f"{delimiter}\n"):
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


def get_tags(dateformat: str = "%Y-%m-%d") -> List[GitTag]:
    inner_delimiter = "---inner_delimiter---"
    formatter = (
        f'"%(refname:lstrip=2){inner_delimiter}'
        f"%(objectname){inner_delimiter}"
        f'%(committerdate:format:{dateformat})"'
    )
    c = cmd.run(f"git tag --format={formatter} --sort=-committerdate")
    if c.err or not c.out:
        return []

    git_tags = [GitTag(*line.split(inner_delimiter)) for line in c.out.split("\n")[:-1]]
    return git_tags


def tag_exist(tag: str) -> bool:
    c = cmd.run(f"git tag --list {tag}")
    return tag in c.out


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
    """Check if staing is clean."""
    c = cmd.run("git diff --no-ext-diff --name-only")
    c_cached = cmd.run("git diff --no-ext-diff --cached --name-only")
    return not (bool(c.out) or bool(c_cached.out))


def is_git_project() -> bool:
    c = cmd.run("git rev-parse --is-inside-work-tree")
    if c.out.strip() == "true":
        return True
    return False
