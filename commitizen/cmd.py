from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING, NamedTuple

from charset_normalizer import from_bytes

from commitizen.exceptions import CharacterSetDecodeError

if TYPE_CHECKING:
    from collections.abc import Mapping


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
        pass

    charset_match = from_bytes(bytes_).best()
    if charset_match is None:
        raise CharacterSetDecodeError()
    try:
        return bytes_.decode(charset_match.encoding)
    except UnicodeDecodeError as e:
        raise CharacterSetDecodeError() from e


def run(cmd: str, env: Mapping[str, str] | None = None) -> Command:
    """Run a command in a subprocess and capture stdout and stderr

    Args:
        cmd: The command to run
        env: Extra environment variables to define in the subprocess. Defaults to None.

    Returns:
        Command: _description_
    """
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


def run_interactive(cmd: str, env: Mapping[str, str] | None = None) -> int:
    """Run a command in a subprocess without redirecting stdin, stdout, or stderr

    Args:
        cmd: The command to run
        env: Extra environment variables to define in the subprocess. Defaults to None.

    Returns:
        subprocess returncode
    """
    if env is not None:
        env = {**os.environ, **env}
    return subprocess.run(cmd, shell=True, env=env).returncode
