from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from typing import NamedTuple

from charset_normalizer import from_bytes

from commitizen.exceptions import CharacterSetDecodeError


class Command(NamedTuple):
    out: str
    err: str
    stdout: bytes
    stderr: bytes
    return_code: int


def _try_decode(bytes_: bytes) -> str:
    try:
        return bytes_.decode("utf-8")
    except UnicodeDecodeError:
        charset_match = from_bytes(bytes_).best()
        if charset_match is None:
            raise CharacterSetDecodeError()
        try:
            return bytes_.decode(charset_match.encoding)
        except UnicodeDecodeError as e:
            raise CharacterSetDecodeError() from e


def run(cmd: str, env: Mapping[str, str] | None = None) -> Command:
    if env is not None:
        env = {**os.environ, **env}
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=env,
    )
    stdout, stderr = process.communicate()
    return_code = process.returncode
    return Command(
        _try_decode(stdout),
        _try_decode(stderr),
        stdout,
        stderr,
        return_code,
    )
