from __future__ import annotations

from commitizen.providers.base_provider import TomlProvider


class Pep621Provider(TomlProvider):
    """
    PEP-621 version management
    """

    filename = "pyproject.toml"
