# Using Commitizen with Docker

Commitizen provides official Docker images hosted on GitHub Container Registry (GHCR), making it easy to use Commitizen in containerized environments without needing Python or pip installed on your host machine.

## Quick Start

### Pull the Latest Image

```bash
docker pull ghcr.io/commitizen-tools/commitizen:latest
```

### Basic Usage

```bash
# Check version
docker run ghcr.io/commitizen-tools/commitizen:latest version

# Get help
docker run ghcr.io/commitizen-tools/commitizen:latest --help

# Use with a git repository
docker run -v $(pwd):/workspace ghcr.io/commitizen-tools/commitizen:latest check
```

## Image Details

### Base Image

- **Base**: Python 3.13 slim (Debian)
- **Architecture**: Multi-arch (amd64, arm64)
- **Size**: Optimized with multi-stage build

### Included Tools

- Python 3.13
- Commitizen (from PyPI)
- Git (required for Commitizen operations)

### Entry Point

The container entry point is set to `cz`, so you can pass commands directly:

```bash
# These are equivalent:
docker run ghcr.io/commitizen-tools/commitizen:latest version
docker run --entrypoint cz ghcr.io/commitizen-tools/commitizen:latest version
```
