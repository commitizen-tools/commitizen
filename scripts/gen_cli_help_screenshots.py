import os
import subprocess
from itertools import chain
from pathlib import Path

from rich.console import Console

from commitizen.cli import data


def gen_cli_help_screenshots() -> None:
    """Generate the screenshot for help message on each cli command and save them as svg files."""
    images_root = Path(__file__).parent.parent / "docs" / "images" / "cli_help"
    images_root.mkdir(parents=True, exist_ok=True)

    cz_commands = (
        command["name"] if isinstance(command["name"], str) else command["name"][0]
        for command in data["subcommands"]["commands"]
    )
    for cmd in chain(
        ["cz --help"], (f"cz {cz_command} --help" for cz_command in cz_commands)
    ):
        file_name = f"{cmd.replace(' ', '_').replace('-', '_')}.svg"
        _export_cmd_as_svg(cmd, images_root / file_name)


def _export_cmd_as_svg(cmd: str, file_path: Path) -> None:
    console = Console(record=True, width=80, file=open(os.devnull, "w"))

    print("Processing command:", cmd)

    console.print(f"$ {cmd}")
    stdout = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode("utf-8")
    console.print(stdout)
    console.save_svg(file_path.as_posix(), title="")

    print("Saved to:", file_path.as_posix())


if __name__ == "__main__":
    gen_cli_help_screenshots()
