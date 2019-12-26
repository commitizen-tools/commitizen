name: str = "cz_conventional_commits"
# TODO: .cz, setup.cfg, .cz.cfg should be removed in 2.0
config_files: list = ["pyproject.toml", ".cz.toml", ".cz", "setup.cfg", ".cz.cfg"]

DEFAULT_SETTINGS = {
    "name": "cz_conventional_commits",
    "version": None,
    "version_files": [],
    "tag_format": None,  # example v$version
    "bump_message": None,  # bumped v$current_version to $new_version
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
