"""File line endings based on the `core.eol` git setting."""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache

from commitizen import cmd


class EOLType(Enum):
    """The EOL type from `git config core.eol`."""

    LF = "lf"
    CRLF = "crlf"
    NATIVE = "native"

    @classmethod
    def for_open(cls) -> str:
        c = cmd.run(["git", "config", "core.eol"])
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


def smart_open(*args, **kwargs):  # type: ignore[no-untyped-def,unused-ignore] # noqa: ANN201
    """Open a file with the EOL style determined from Git."""
    return open(*args, newline=EOLType.for_open(), **kwargs)
