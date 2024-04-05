import os
import subprocess
from pathlib import Path

from rich.console import Console

from commitizen.cli import data

project_root = Path(__file__).parent.parent.absolute()
images_root = project_root / Path("docs") / Path("images") / Path("cli_help")


def gen_cli_help_screenshots() -> None:
    """Generate the screenshot for help message on each cli command and save them as svg files."""
    if not os.path.exists(images_root):
        os.makedirs(images_root)
        print(f"Created {images_root}")

    help_cmds = _list_help_cmds()
    for cmd in help_cmds:
        file_name = f"{cmd.replace(' ', '_').replace('-', '_')}.svg"
        _export_cmd_as_svg(cmd, f"{images_root}/{file_name}")


def _list_help_cmds() -> list[str]:
    cmds = [f"{data['prog']} --help"] + [
        f"{data['prog']} {sub_c['name'] if isinstance(sub_c['name'], str) else sub_c['name'][0]} --help"
        for sub_c in data["subcommands"]["commands"]
    ]

    return cmds


def _export_cmd_as_svg(cmd: str, file_name: str) -> None:
    stdout = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode("utf-8")
    console = Console(record=True, width=80)
    console.print(f"$ {cmd}\n{stdout}")
    console.save_svg(file_name, title="")


if __name__ == "__main__":
    gen_cli_help_screenshots()
