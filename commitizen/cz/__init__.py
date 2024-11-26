from __future__ import annotations

import importlib
import pkgutil
import sys
import warnings
from collections.abc import Iterable

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from commitizen.cz.base import BaseCommitizen


def discover_plugins(
    path: Iterable[str] | None = None,
) -> dict[str, type[BaseCommitizen]]:
    """Discover commitizen plugins on the path

    Args:
        path (Path, optional): If provided, 'path' should be either None or a list of paths to look for
    modules in. If path is None, all top-level modules on sys.path.. Defaults to None.

    Returns:
        Dict[str, Type[BaseCommitizen]]: Registry with found plugins
    """
    for _, name, _ in pkgutil.iter_modules(path):
        if name.startswith("cz_"):
            mod = importlib.import_module(name)
            if hasattr(mod, "discover_this"):
                warnings.warn(
                    UserWarning(
                        f"Legacy plugin '{name}' has been ignored: please expose it the 'commitizen.plugin' entrypoint"
                    )
                )

    return {
        ep.name: ep.load() for ep in metadata.entry_points(group="commitizen.plugin")
    }


registry: dict[str, type[BaseCommitizen]] = discover_plugins()
