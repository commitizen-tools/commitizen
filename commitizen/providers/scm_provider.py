from __future__ import annotations

from commitizen.git import get_tags
from commitizen.providers.base_provider import VersionProvider
from commitizen.tags import TagRules


class ScmProvider(VersionProvider):
    """
    A provider fetching the current/last version from the repository history

    The version is fetched using `git describe` and is never set.

    It is meant for `setuptools-scm` or any package manager `*-scm` provider.
    """

    def get_version(self) -> str:
        rules = TagRules.from_settings(self.config.settings)
        tags = get_tags(reachable_only=True)
        version_tags = rules.get_version_tags(tags)
        version = max((rules.extract_version(t) for t in version_tags), default=None)
        return str(version) if version is not None else "0.0.0"

    def set_version(self, version: str) -> None:
        # Not necessary
        pass
