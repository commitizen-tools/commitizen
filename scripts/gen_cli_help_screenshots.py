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


def gen_interactive_screenshots() -> None:
    """Generate GIF screenshots for interactive commands using VHS."""
    images_root = Path(__file__).parent.parent / "docs" / "images"

    vhs_files = ["init.tape", "commit.tape"]

    for vhs_file in vhs_files:
        vhs_path = images_root / vhs_file
        if vhs_path.exists():
            print(f"Processing VHS file: {vhs_file}")
            try:
                subprocess.run(
                    ["vhs", str(vhs_path)],
                    check=True,
                    cwd=images_root.as_posix(),
                )
                gif_file = vhs_file.replace(".tape", ".gif")
                print(f"✓ Generated {gif_file} from {vhs_file}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Error processing {vhs_file}: {e}")
                raise
            except FileNotFoundError:
                print(
                    "VHS is not installed. Please install it from: "
                    "https://github.com/charmbracelet/vhs"
                )
                raise
        else:
            print(f"Warning: {vhs_file} not found, skipping")


if __name__ == "__main__":
    gen_cli_help_screenshots()
    gen_interactive_screenshots()
