name: str = "cz_conventional_commits"
# TODO: .cz, setup.cfg, .cz.cfg should be removed in 2.0
long_term_support_config_files: list = ["pyproject.toml", ".cz.toml"]
deprcated_config_files: list = [".cz", "setup.cfg", ".cz.cfg"]
config_files: list = long_term_support_config_files + deprcated_config_files

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
