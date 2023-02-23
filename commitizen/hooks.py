from __future__ import annotations

import os

from commitizen import cmd, out
from commitizen.exceptions import RunHookError


def run(hooks, _env_prefix="CZ_", **env):
    if isinstance(hooks, str):
        hooks = [hooks]

    for hook in hooks:
        out.info(f"Running hook '{hook}'")

        c = cmd.run(hook, env=_format_env(_env_prefix, env))

        if c.out:
            out.write(c.out)
        if c.err:
            out.error(c.err)

        if c.return_code != 0:
            raise RunHookError(f"Running hook '{hook}' failed")


def _format_env(prefix: str, env: dict[str, str]) -> dict[str, str]:
    """_format_env() prefixes all given environment variables with the given
    prefix so it can be passed directly to cmd.run()."""
    penv = dict(os.environ)
    for name, value in env.items():
        name = prefix + name.upper()
        value = str(value) if value is not None else ""
        penv[name] = value

    return penv
