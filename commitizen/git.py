import os
from tempfile import NamedTemporaryFile
from commitizen import cmd


def tag(tag: str):
    c = cmd.run(f"git tag {tag}")
    return c


def commit(message: str):
    f = NamedTemporaryFile("wb", delete=False)
    f.write(message.encode("utf-8"))
    f.close()
    os.unlink(f.name)
    c = cmd.run(f"git commit -F {f.name}")
    return c


def filter_commits(start: str, end: str = "HEAD") -> list:
    c = cmd.run(f"git log --pretty=format:'%s' {start}...{end}")
    if not c.err:
        return []
    return c.out.split("\n")
