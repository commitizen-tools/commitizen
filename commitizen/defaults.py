name: str = "cz_conventional_commits"
config_files: list = ["pyproject.toml", ".cz", "setup.cfg", ".cz.cfg"]

# Available settings
settings: dict = {
    "name": name,
    "version": None,
    "files": [],
    "tag_format": None,  # example v$version
}
