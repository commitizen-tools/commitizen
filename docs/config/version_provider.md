# Version Providers

Version providers are the mechanism by which Commitizen reads and writes version information in your project.

They abstract away the details of where and how version numbers are stored, allowing Commitizen to work seamlessly with different project types and package management systems.

## Overview

By default, Commitizen uses the `commitizen` provider, which stores the version in your Commitizen configuration file.
However, you can configure Commitizen to use any available provider that matches your project's setup.
This is particularly useful when you want Commitizen to manage versions in the same location as your package manager (e.g., `package.json` for Node.js projects, `pyproject.toml` for Python projects).

## Built-in Providers

Commitizen includes several built-in version providers for common package management formats:

### `commitizen` (Default)

The default version provider stores and retrieves the version from your Commitizen configuration file (e.g., `pyproject.toml`, `.cz.toml`, etc.).

**Use when:**

- You want to keep version management separate from your package manager
- Your project doesn't use a standard package manager
- You need maximum flexibility in version management

**Configuration:**
```toml
[tool.commitizen]
version_provider = "commitizen"
version = "0.1.0"  # Required when using this provider
```

### `scm`

Fetches the version from Git tags using `git describe`. This provider **only reads** version information and never writes it back to files. It's designed to work with tools like `setuptools-scm` or other package manager `*-scm` plugins that derive version numbers from Git history.

**Use when:**

- You're using `setuptools-scm` or similar tools
- You want version numbers derived from Git tags
- You don't want Commitizen to modify any files for version management

**Configuration:**
```toml
[tool.commitizen]
version_provider = "scm"
# No version field needed - it's read from Git tags
```

!!! note
    The `scm` provider is read-only. When you run `cz bump`, it will create a Git tag but won't update any files. This is intentional and works well with tools that derive versions from Git tags.

### `pep621`

Manages version in `pyproject.toml` under the `project.version` field, following [PEP 621](https://peps.python.org/pep-0621/) standards.

**Use when:**

- You're using a modern Python project with PEP 621-compliant `pyproject.toml`
- You want version management integrated with your Python project metadata

**Configuration:**
```toml
[tool.commitizen]
version_provider = "pep621"
```

**Example `pyproject.toml`:**
```toml
[project]
name = "my-package"
version = "0.1.0"  # Managed by Commitizen
```

### `poetry`

Manages version in `pyproject.toml` under the `tool.poetry.version` field, which is used by the [Poetry](https://python-poetry.org/) package manager. This approach is recommended only for users running Poetry versions earlier than 2.0 or relying on Poetry-specific features. For most users on Poetry 2.0 or later, it is recommended to use `pep621` instead. [Read More](https://python-poetry.org/docs/main/managing-dependencies/)

**Use when:**

- You're using Poetry < 2.0 as your Python package manager
- You're using Poetry >= 2.0 as your Python package manager, but don't need poetry-specific features
- You want Commitizen to manage the version that Poetry uses

**Configuration:**
```toml
[tool.commitizen]
version_provider = "poetry"
```

**Example `pyproject.toml`:**
```toml
[tool.poetry]
name = "my-package"
version = "0.1.0"  # Managed by Commitizen
```

### `uv`

Manages version in both `pyproject.toml` (`project.version`) and `uv.lock` (`package.version` for the matching package name). This ensures consistency between your project metadata and lock file.


!!! note
    Even though uv follows PEP 621 format, `pep621` does not manage the version in `uv.lock`. `uv` is still suggested for uv users.

**Use when:**

- You're using `uv` as your Python package manager
- You want version synchronization between `pyproject.toml` and `uv.lock`

**Configuration:**
```toml
[tool.commitizen]
version_provider = "uv"
```

### `cargo`

Manages version in both `Cargo.toml` (`package.version`) and `Cargo.lock` (`package.version` for the matching package name). This ensures consistency between your Rust project's manifest and lock file.

**Use when:**

- You're working with a Rust project using Cargo
- You want Commitizen to manage Rust package versions

**Configuration:**
```toml
[tool.commitizen]
version_provider = "cargo"
```

**Example `Cargo.toml`:**
```toml
[package]
name = "my-crate"
version = "0.1.0"  # Managed by Commitizen
```

### `npm`

Manages version in `package.json` and optionally synchronizes with `package-lock.json` and `npm-shrinkwrap.json` if they exist.

**Use when:**

- You're working with a Node.js/JavaScript project
- You want Commitizen to manage npm package versions

**Configuration:**
```toml
[tool.commitizen]
version_provider = "npm"
```

**Example `package.json`:**
```json
{
  "name": "my-package",
  "version": "0.1.0"
}
```

### `composer`

Manages version in `composer.json` under the `version` field, used by PHP's Composer package manager.

**Use when:**

- You're working with a PHP project using Composer
- You want Commitizen to manage Composer package versions

**Configuration:**
```toml
[tool.commitizen]
version_provider = "composer"
```

**Example `composer.json`:**
```json
{
  "name": "vendor/package",
  "version": "0.1.0"
}
```

## Provider Comparison Table

| Provider     | File(s) Modified                    | Read-Only | Best For                          |
| ------------ | ----------------------------------- | --------- | --------------------------------- |
| `commitizen` | Commitizen config file              | No        | General use, flexible projects    |
| `scm`        | None (reads from Git tags)          | Yes       | `setuptools-scm` users            |
| `pep621`     | `pyproject.toml` (`project.version`) | No        | Modern Python (PEP 621)           |
| `poetry`     | `pyproject.toml` (`tool.poetry.version`) | No    | Poetry projects                   |
| `uv`         | `pyproject.toml` + `uv.lock`        | No        | uv package manager                |
| `cargo`      | `Cargo.toml` + `Cargo.lock`          | No        | Rust/Cargo projects               |
| `npm`        | `package.json` (+ lock files)       | No        | Node.js/npm projects              |
| `composer`   | `composer.json`                     | No        | PHP/Composer projects             |

## Creating Custom Version Providers

If none of the built-in providers meet your needs, you can create a custom version provider by extending the `VersionProvider` base class and registering it as a plugin.

### Step 1: Create Your Provider Class

Create a Python file (e.g., `my_provider.py`) that extends `VersionProvider`:

```python title="my_provider.py"
from pathlib import Path
from commitizen.providers import VersionProvider


class MyProvider(VersionProvider):
    """
    Custom version provider that reads/writes from a VERSION file.
    """

    def get_version(self) -> str:
        """Read version from VERSION file."""
        version_file = Path("VERSION")
        if not version_file.is_file():
            return "0.0.0"
        return version_file.read_text().strip()

    def set_version(self, version: str) -> None:
        """Write version to VERSION file."""
        version_file = Path("VERSION")
        version_file.write_text(f"{version}\n")
```

### Step 2: Register as an Entry Point

Register your provider using the `commitizen.provider` entry point. You can do this in your `setup.py`, `setup.cfg`, or `pyproject.toml`:

**Using `pyproject.toml` (recommended):**

```toml title="pyproject.toml"
[project]
name = "my-commitizen-provider"
version = "0.1.0"
dependencies = ["commitizen"]

[project.entry-points."commitizen.provider"]
my-provider = "my_provider:MyProvider"
```

**Using `setup.py` (for legacy setup):**

```python title="setup.py"
from setuptools import setup

setup(
    name="my-commitizen-provider",
    version="0.1.0",
    py_modules=["my_provider"],
    install_requires=["commitizen"],
    entry_points={
        "commitizen.provider": [
            "my-provider = my_provider:MyProvider",
        ]
    },
)
```

### Step 3: Install and Use

1. Install your provider package:

    - Once your custom Commitizen provider is packaged and published (for example, to PyPI), install it like any standard Python package:

        ```bash
        pip install my-commitizen-provider
        ```

    - If you want to use the provider directly from the current project source (during development), install it in editable mode ([See pip documentation](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e)):

        ```bash
        pip install -e .
        ```

2. Configure Commitizen to use your provider:
   ```toml
   [tool.commitizen]
   version_provider = "my-provider"
   ```

### Provider Implementation Guidelines

When creating a custom provider, keep these guidelines in mind:

- **`get_version()`** should return a string representing the current version. If no version is found, you can return `"0.0.0"` or raise an appropriate exception.
- **`set_version(version: str)`** should write the version to your chosen storage location. The version string will be properly formatted according to your `version_scheme` setting.
- The provider has access to `self.config`, which is a `BaseConfig` instance containing all Commitizen settings.
- For file-based providers, consider using the `FileProvider` or `JsonProvider`/`TomlProvider` base classes from `commitizen.providers.base_provider` to simplify implementation.

### Example: JSON-based Provider

Here's a more complete example using the `JsonProvider` base class:

```python title="json_version_provider.py"
from commitizen.providers.base_provider import JsonProvider


class JsonVersionProvider(JsonProvider):
    """
    Version provider that uses a custom version.json file.
    """

    filename = "version.json"

    def get(self, document):
        """Extract version from JSON document."""
        return document["version"]

    def set(self, document, version):
        """Set version in JSON document."""
        document["version"] = version
```

This example leverages the `JsonProvider` base class, which handles file reading, writing, and JSON parsing automatically.

## Choosing the Right Provider

Select a version provider based on your project's characteristics:

- **Python projects**
    - **with `uv`**: Use `uv`
    - **with `pyproject.toml` that follows PEP 621**: Use `pep621`
    - **with Poetry**: Use `poetry`
    - **setuptools-scm**: Use `scm`
- **Rust projects**: Use `cargo`
- **Node.js projects**: Use `npm`
- **PHP projects**: Use `composer`
- **Other cases or custom needs**: Use `commitizen` (default) or create a custom provider

Remember that you can always use `version_files` in combination with any provider to update additional files during version bumps, regardless of which provider you choose for reading/writing the primary version.
