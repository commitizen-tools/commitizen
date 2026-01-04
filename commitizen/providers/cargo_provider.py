from __future__ import annotations

import fnmatch
import glob
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from tomlkit import TOMLDocument, dumps, parse
from tomlkit.exceptions import NonExistentKey

from commitizen.providers.base_provider import TomlProvider

if TYPE_CHECKING:
    from collections.abc import Iterable

    from tomlkit.items import AoT


DictLike = dict[str, Any]


class CargoProvider(TomlProvider):
    """Cargo version management for virtual workspace manifests + version.workspace=true members."""

    filename = "Cargo.toml"
    lock_filename = "Cargo.lock"

    @property
    def lock_file(self) -> Path:
        return Path(self.lock_filename)

    def get(self, document: TOMLDocument) -> str:
        t = _root_version_table(document)
        v = t.get("version")
        if not isinstance(v, str):
            raise TypeError("expected root version to be a string")
        return v

    def set(self, document: TOMLDocument, version: str) -> None:
        _root_version_table(document)["version"] = version

    def set_version(self, version: str) -> None:
        super().set_version(version)
        if self.lock_file.exists():
            self.set_lock_version(version)

    def set_lock_version(self, version: str) -> None:
        cargo_toml = parse(self.file.read_text())
        cargo_lock = parse(self.lock_file.read_text())
        packages = cargo_lock["package"]
        if TYPE_CHECKING:
            assert isinstance(packages, AoT)

        root_pkg = _table_get(cargo_toml, "package")
        if root_pkg is not None:
            name = root_pkg.get("name")
            if isinstance(name, str):
                _lock_set_versions(packages, {name}, version)
            self.lock_file.write_text(dumps(cargo_lock))
            return

        ws = _table_get(cargo_toml, "workspace") or {}
        members = cast("list[str]", ws.get("members", []) or [])
        excludes = cast("list[str]", ws.get("exclude", []) or [])
        inheriting = _workspace_inheriting_member_names(members, excludes)
        _lock_set_versions(packages, inheriting, version)
        self.lock_file.write_text(dumps(cargo_lock))


def _table_get(doc: TOMLDocument, key: str) -> DictLike | None:
    """Return a dict-like table for `key` if present, else None (type-safe for Pylance)."""
    try:
        v = doc[key]  # tomlkit returns Container/Table-like; typing is loose
    except NonExistentKey:
        return None
    return cast("DictLike", v) if hasattr(v, "get") else None


def _root_version_table(doc: TOMLDocument) -> DictLike:
    """Prefer [workspace.package]; fallback to [package]."""
    ws = _table_get(doc, "workspace")
    if ws is not None:
        pkg = ws.get("package")
        if hasattr(pkg, "get"):
            return cast("DictLike", pkg)
    pkg = _table_get(doc, "package")
    if pkg is None:
        raise NonExistentKey("expected either [workspace.package] or [package]")
    return pkg


def _is_workspace_inherited_version(v: Any) -> bool:
    return hasattr(v, "get") and cast("DictLike", v).get("workspace") is True


def _iter_member_dirs(
    members: Iterable[str], excludes: Iterable[str]
) -> Iterable[Path]:
    for pat in members:
        for p in glob.glob(pat, recursive=True):
            if any(fnmatch.fnmatch(p, ex) for ex in excludes):
                continue
            yield Path(p)


def _workspace_inheriting_member_names(
    members: Iterable[str], excludes: Iterable[str]
) -> set[str]:
    out: set[str] = set()
    for d in _iter_member_dirs(members, excludes):
        cargo_file = d / "Cargo.toml"
        if not cargo_file.exists():
            continue
        pkg = parse(cargo_file.read_text()).get("package")
        if not hasattr(pkg, "get"):
            continue
        pkgd = cast("DictLike", pkg)
        if _is_workspace_inherited_version(pkgd.get("version")):
            name = pkgd.get("name")
            if isinstance(name, str):
                out.add(name)
    return out


def _lock_set_versions(packages: Any, names: set[str], version: str) -> None:
    if not names:
        return
    for i, p in enumerate(packages):
        if getattr(p, "get", None) and p.get("name") in names:
            packages[i]["version"] = version  # type: ignore[index]
