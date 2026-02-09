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
        if self.lock_file.is_file():
            self.set_lock_version(version)

    def set_lock_version(self, version: str) -> None:
        cargo_toml_content = parse(self.file.read_text())
        cargo_lock_content = parse(self.lock_file.read_text())
        packages = cargo_lock_content["package"]

        if TYPE_CHECKING:
            assert isinstance(packages, AoT)

        root_pkg = _table_get(cargo_toml_content, "package")
        if root_pkg is not None:
            name = root_pkg.get("name")
            if isinstance(name, str):
                _lock_set_versions(packages, {name}, version)
            self.lock_file.write_text(dumps(cargo_lock_content))
            return

        ws = _table_get(cargo_toml_content, "workspace") or {}
        member_globs = cast("list[str]", ws.get("members", []) or [])
        exclude_globs = cast("list[str]", ws.get("exclude", []) or [])
        inheriting = _workspace_inheriting_member_names(member_globs, exclude_globs)
        _lock_set_versions(packages, inheriting, version)
        self.lock_file.write_text(dumps(cargo_lock_content))


def _table_get(doc: TOMLDocument, key: str) -> DictLike | None:
    """Get a TOML table by key as a dict-like object.

    Returns:
        The value at `doc[key]` cast to a dict-like table (supports `.get`) if it
        exists and is table/container-like; otherwise returns None.

    Rationale:
        tomlkit returns loosely-typed Container/Table objects; using a small
        helper keeps call sites readable and makes type-checkers happier.
    """
    try:
        value = doc[key]
    except NonExistentKey:
        return None
    return cast("DictLike", value) if hasattr(value, "get") else None


def _root_version_table(doc: TOMLDocument) -> DictLike:
    """Return the table that owns the "root" version field.

    This provider supports two layouts:

    1) Workspace virtual manifests:
            [workspace.package]
            version = "x.y.z"

    2) Regular crate（non-workspace root manifest）:
            [package]
            version = "x.y.z"

    The selected table is where `get()` reads from and `set()` writes to.
    """
    workspace_table = _table_get(doc, "workspace")
    if workspace_table is not None:
        workspace_package_table = workspace_table.get("package")
        if hasattr(workspace_package_table, "get"):
            return cast("DictLike", workspace_package_table)

    package_table = _table_get(doc, "package")
    if package_table is None:
        raise NonExistentKey("expected either [workspace.package] or [package]")
    return package_table


def _is_workspace_inherited_version(v: Any) -> bool:
    return hasattr(v, "get") and cast("DictLike", v).get("workspace") is True


def _iter_member_dirs(
    member_globs: Iterable[str], exclude_globs: Iterable[str]
) -> Iterable[Path]:
    """Yield workspace member directories matched by `member_globs`, excluding `exclude_globs`.

    Cargo workspaces define members/exclude as glob patterns (e.g. "crates/*").
    This helper expands those patterns and yields the corresponding directories
    as `Path` objects, skipping any matches that satisfy an exclude glob.

    Kept as a helper to make call sites read as domain logic ("iterate member dirs")
    rather than glob/filter plumbing.
    """
    for member_glob in member_globs:
        for match in glob.glob(member_glob, recursive=True):
            if any(fnmatch.fnmatch(match, ex) for ex in exclude_globs):
                continue
            yield Path(match)


def _workspace_inheriting_member_names(
    members: Iterable[str], excludes: Iterable[str]
) -> set[str]:
    """Return workspace member crate names that inherit the workspace version.

    A member is considered "inheriting" when its Cargo.toml has:
        [package]
        version.workspace = true

    This scans `members` globs (respecting `excludes`) and returns the set of
    `[package].name` values for matching crates. Missing/invalid Cargo.toml files
    are ignored.
    """
    inheriting_member_names: set[str] = set()
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
                inheriting_member_names.add(name)
    return inheriting_member_names


def _lock_set_versions(packages: Any, package_names: set[str], version: str) -> None:
    """Update Cargo.lock package entries in-place.

    Args:
        packages: `Cargo.lock` parsed TOML "package" array (AoT-like). Mutated in-place.
        package_names: Set of package names whose `version` field should be updated.
        version: New version string to write.

    Notes:
        We use `enumerate` + index assignment because tomlkit AoT entries may be
        Container-like and direct mutation patterns vary; indexed assignment is
        reliable for updating the underlying document.
    """
    if not package_names:
        return
    for i, pkg_entry in enumerate(packages):
        if getattr(pkg_entry, "get", None) and pkg_entry.get("name") in package_names:
            packages[i]["version"] = version
