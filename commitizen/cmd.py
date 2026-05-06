from __future__ import annotations

import os
import subprocess
import warnings
from typing import TYPE_CHECKING, NamedTuple, overload

from charset_normalizer import from_bytes

from commitizen.exceptions import CharacterSetDecodeError

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


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


def _popen(
    cmd: str | Sequence[str],
    *,
    shell: bool,
    env: Mapping[str, str] | None = None,
) -> Command:
    if env is not None:
        env = {**os.environ, **env}

    process = subprocess.Popen(
        cmd,
        shell=shell,
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


@overload
def run(cmd: str, env: Mapping[str, str] | None = None) -> Command: ...


@overload
def run(cmd: Sequence[str], env: Mapping[str, str] | None = None) -> Command: ...


def run(cmd: str | Sequence[str], env: Mapping[str, str] | None = None) -> Command:
    """Run a command safely without shell interpretation (shell=False).

    Arguments are passed directly to the OS, preventing shell-injection
    vulnerabilities (CWE-78).

    Passing a string is deprecated and will be removed in a future version.
    Use a list of arguments instead, or use run_shell() for shell features.
    """
    if isinstance(cmd, str):
        warnings.warn(
            "Passing a string to cmd.run() is deprecated and will be removed in v5. "
            "Use a list of arguments instead, or use cmd.run_shell() explicitly.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _popen(cmd, shell=True, env=env)
    return _popen(cmd, shell=False, env=env)


def run_shell(cmd: str, env: Mapping[str, str] | None = None) -> Command:
    """Run a command string via the system shell (shell=True).

    Only use this for cases that intentionally require shell features
    (e.g., user-defined hooks with pipes/redirects). Never pass
    untrusted/user-controlled values into *cmd*.

    Related: CWE-78 (OS Command Injection),
    https://github.com/commitizen-tools/commitizen/issues/1918
    """
    return _popen(cmd, shell=True, env=env)
