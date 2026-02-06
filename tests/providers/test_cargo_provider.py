from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from commitizen.providers import get_provider
from commitizen.providers.cargo_provider import CargoProvider

if TYPE_CHECKING:
    from commitizen.config.base_config import BaseConfig

CARGO_TOML = """\
[package]
name = "whatever"
version = "0.1.0"
"""

CARGO_TOML_EXPECTED = """\
[package]
name = "whatever"
version = "42.1"
"""

CARGO_WORKSPACE_TOML = """\
[workspace]
members = ["member1", "folder/member2", "crates/*"]
exclude = ["crates/member4", "folder/member5"]

[workspace.package]
version = "0.1.0"
"""

CARGO_WORKSPACE_MEMBERS = [
    {
        "path": "member1",
        "content": """\
[package]
name = "member1"
version.workspace = true
""",
    },
    {
        "path": "folder/member2",
        "content": """\
[package]
name = "member2"
version.workspace = "1.1.1"
""",
    },
    {
        "path": "crates/member3",
        "content": """\
[package]
name = "member3"
version.workspace = true
""",
    },
    {
        "path": "crates/member4",
        "content": """\
[package]
name = "member4"
version.workspace = "2.2.2"
""",
    },
    {
        "path": "folder/member5",
        "content": """\
[package]
name = "member5"
version.workspace = "3.3.3"
""",
    },
]


CARGO_WORKSPACE_TOML_EXPECTED = """\
[workspace]
members = ["member1", "folder/member2", "crates/*"]
exclude = ["crates/member4", "folder/member5"]

[workspace.package]
version = "42.1"
"""

CARGO_LOCK = """\
[[package]]
name = "whatever"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]
"""

CARGO_LOCK_EXPECTED = """\
[[package]]
name = "whatever"
version = "42.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]
"""

CARGO_WORKSPACE_LOCK = """\
[[package]]
name = "member1"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member2"
version = "1.1.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member3"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member4"
version = "2.2.2"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member5"
version = "3.3.3"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]
"""

CARGO_WORKSPACE_LOCK_EXPECTED = """\
[[package]]
name = "member1"
version = "42.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member2"
version = "1.1.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member3"
version = "42.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member4"
version = "2.2.2"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]

[[package]]
name = "member5"
version = "3.3.3"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]
"""


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (CARGO_TOML, CARGO_TOML_EXPECTED),
        (CARGO_WORKSPACE_TOML, CARGO_WORKSPACE_TOML_EXPECTED),
    ],
)
def test_cargo_provider(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = CargoProvider.filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "cargo"

    provider = get_provider(config)
    assert isinstance(provider, CargoProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(expected)


@pytest.mark.parametrize(
    ("toml_content", "lock_content", "toml_expected", "lock_expected"),
    [
        (
            CARGO_TOML,
            CARGO_LOCK,
            CARGO_TOML_EXPECTED,
            CARGO_LOCK_EXPECTED,
        ),
        (
            CARGO_WORKSPACE_TOML,
            CARGO_WORKSPACE_LOCK,
            CARGO_WORKSPACE_TOML_EXPECTED,
            CARGO_WORKSPACE_LOCK_EXPECTED,
        ),
    ],
)
def test_cargo_provider_with_lock(
    config: BaseConfig,
    chdir: Path,
    toml_content: str,
    lock_content: str,
    toml_expected: str,
    lock_expected: str,
):
    filename = CargoProvider.filename
    file = chdir / filename
    file.write_text(dedent(toml_content))

    # Create workspace members
    os.mkdir(chdir / "crates")
    os.mkdir(chdir / "folder")
    for i in range(0, 5):
        member_folder = Path(CARGO_WORKSPACE_MEMBERS[i]["path"])
        os.mkdir(member_folder)
        member_file = member_folder / "Cargo.toml"
        member_file.write_text(dedent(CARGO_WORKSPACE_MEMBERS[i]["content"]))

    lock_filename = CargoProvider.lock_filename
    lock_file = chdir / lock_filename
    lock_file.write_text(dedent(lock_content))
    config.settings["version_provider"] = "cargo"

    provider = get_provider(config)
    assert isinstance(provider, CargoProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(toml_expected)
    assert lock_file.read_text() == dedent(lock_expected)


def test_cargo_provider_workspace_member_without_version_key(
    config: BaseConfig,
    chdir: Path,
):
    """Test workspace member that has no version key at all (should not crash)."""
    workspace_toml = """\
[workspace]
members = ["member_without_version"]

[workspace.package]
version = "0.1.0"
"""

    # Create a member that has no version key at all
    member_content = """\
[package]
name = "member_without_version"
# No version key - this should trigger NonExistentKey exception
"""

    lock_content = """\
[[package]]
name = "member_without_version"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
"""

    expected_workspace_toml = """\
[workspace]
members = ["member_without_version"]

[workspace.package]
version = "42.1"
"""

    expected_lock_content = """\
[[package]]
name = "member_without_version"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
"""

    # Create the workspace file
    filename = CargoProvider.filename
    file = chdir / filename
    file.write_text(dedent(workspace_toml))

    # Create the member directory and file
    os.mkdir(chdir / "member_without_version")
    member_file = chdir / "member_without_version" / "Cargo.toml"
    member_file.write_text(dedent(member_content))

    # Create the lock file
    lock_filename = CargoProvider.lock_filename
    lock_file = chdir / lock_filename
    lock_file.write_text(dedent(lock_content))

    config.settings["version_provider"] = "cargo"

    provider = get_provider(config)
    assert isinstance(provider, CargoProvider)
    assert provider.get_version() == "0.1.0"

    # This should not crash even though the member has no version key
    provider.set_version("42.1")
    assert file.read_text() == dedent(expected_workspace_toml)
    # The lock file should remain unchanged since the member doesn't inherit workspace version
    assert lock_file.read_text() == dedent(expected_lock_content)


def test_cargo_provider_workspace_member_without_workspace_key(
    config: BaseConfig,
    chdir: Path,
):
    """Test workspace member that has version key but no workspace subkey."""
    workspace_toml = """\
[workspace]
members = ["member_without_workspace"]

[workspace.package]
version = "0.1.0"
"""

    # Create a member that has version as a table but no workspace subkey
    # This should trigger NonExistentKey when trying to access version["workspace"]
    member_content = """\
[package]
name = "member_without_workspace"

[package.version]
# Has version table but no workspace key - should trigger NonExistentKey
"""

    lock_content = """\
[[package]]
name = "member_without_workspace"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
"""

    expected_workspace_toml = """\
[workspace]
members = ["member_without_workspace"]

[workspace.package]
version = "42.1"
"""

    expected_lock_content = """\
[[package]]
name = "member_without_workspace"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
"""

    # Create the workspace file
    filename = CargoProvider.filename
    file = chdir / filename
    file.write_text(dedent(workspace_toml))

    # Create the member directory and file
    os.mkdir(chdir / "member_without_workspace")
    member_file = chdir / "member_without_workspace" / "Cargo.toml"
    member_file.write_text(dedent(member_content))

    # Create the lock file
    lock_filename = CargoProvider.lock_filename
    lock_file = chdir / lock_filename
    lock_file.write_text(dedent(lock_content))

    config.settings["version_provider"] = "cargo"

    provider = get_provider(config)
    assert isinstance(provider, CargoProvider)
    assert provider.get_version() == "0.1.0"

    # This should not crash even though the member has no version.workspace key
    provider.set_version("42.1")
    assert file.read_text() == dedent(expected_workspace_toml)
    # The lock file should remain unchanged since the member doesn't inherit workspace version
    assert lock_file.read_text() == dedent(expected_lock_content)
