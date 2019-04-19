name: str = "cz_conventional_commits"
config_files: list = ["pyproject.toml", ".cz", "setup.cfg", ".cz.cfg"]

# Available settings
settings: dict = {
    "name": name,
    "version": None,
    "files": [],
    "tag_format": None,  # example v$version
}

MAJOR = "MAJOR"
MINOR = "MINOR"
PATCH = "PATCH"

bump_pattern = r"^(BREAKING CHANGE|feat)"
bump_map = {"BREAKING CHANGE": MAJOR, "feat": MINOR}
