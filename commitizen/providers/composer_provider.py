from __future__ import annotations

from commitizen.providers.base_provider import JsonProvider


class ComposerProvider(JsonProvider):
    """
    Composer version management
    """

    filename = "composer.json"
    indent = 4
