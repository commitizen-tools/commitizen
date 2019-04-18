import os
from tempfile import NamedTemporaryFile
from commitizen import cmd


def tag(tag: str):
    c = cmd.run(f"git tag {tag}")
    return c


def commit(message: str, args=""):
    f = NamedTemporaryFile("wb", delete=False)
    f.write(message.encode("utf-8"))
    f.close()
    c = cmd.run(f"git commit {args} -F {f.name}")
    os.unlink(f.name)
    return c


def get_commits(start: str, end: str = "HEAD", from_beginning: bool = False) -> list:

    c = cmd.run(f"git log --pretty=format:%s%n%b {start}...{end}")

    if from_beginning:
        c = cmd.run(f"git log --pretty=format:%s%n%b {end}")

    if not c.out:
        return []
    return c.out.split("\n")


def tag_exist(tag: str) -> bool:
    c = cmd.run(f"git tag --list {tag}")
    return tag in c.out
