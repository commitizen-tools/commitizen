from packaging.version import Version


class SemVerVersion(Version):
    def __str__(self) -> str:
        parts = []

        # Epoch
        if self.epoch != 0:
            parts.append(f"{self.epoch}!")

        # Release segment
        parts.append(".".join(str(x) for x in self.release))

        # Pre-release
        if self.pre is not None:
            pre = "".join(str(x) for x in self.pre)
            parts.append(f"-{pre}")

        # Post-release
        if self.post is not None:
            parts.append(f"-post{self.post}")

        # Development release
        if self.dev is not None:
            parts.append(f"-dev{self.dev}")

        # Local version segment
        if self.local is not None:
            parts.append(f"+{self.local}")

        return "".join(parts)


providers = {
    "pep": Version,
    "semver": SemVerVersion,
}
