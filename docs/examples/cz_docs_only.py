"""Executable custom bump-rule example published in the documentation."""

from __future__ import annotations

from commitizen.cz.conventional_commits import ConventionalCommitsCz


class DocsOnlyPatchCommitizen(ConventionalCommitsCz):
    """Skip version bumps for docs commits while patch-bumping fixes.

    Example:
        Configure the plugin as ``cz_docs_only`` to ignore ``docs:`` commits for
        version bumps while still treating ``fix:`` commits as patch releases.

    Attributes:
        bump_pattern: Extracts the commit types that participate in bump logic.
        bump_map: Maps ``docs`` to no increment and ``fix`` to a patch bump.
    """

    bump_pattern = r"^(docs|fix)(?:\([^()\r\n]*\))?!?:"
    bump_map = {"docs": None, "fix": "PATCH"}
