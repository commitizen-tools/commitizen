name: str = "cz_conventional_commits"
config_files: list = ["pyproject.toml", ".cz", "setup.cfg", ".cz.cfg"]

# Available settings
settings: dict = {
    "name": name,
    "version": None,
    "files": [],
    "tag_format": None,  # example v$version
    "bump_message": None  # bumped v$current_version to $new_version
}

MAJOR = "MAJOR"
MINOR = "MINOR"
PATCH = "PATCH"

bump_pattern = r"^(BREAKING CHANGE|feat|fix|refactor|perf)"
bump_map = {
    "BREAKING CHANGE": MAJOR,
    "feat": MINOR,
    "fix": PATCH,
    "refactor": PATCH,
    "perf": PATCH,
}
bump_message = "bump: version $current_version → $new_version"
