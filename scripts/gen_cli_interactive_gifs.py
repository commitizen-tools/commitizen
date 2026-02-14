import subprocess
from pathlib import Path


def gen_cli_interactive_gifs() -> None:
    """Generate GIF screenshots for interactive commands using VHS."""
    vhs_dir = Path(__file__).parent.parent / "docs" / "images"
    output_dir = Path(__file__).parent.parent / "docs" / "images" / "cli_interactive"
    output_dir.mkdir(parents=True, exist_ok=True)

    vhs_files = list(vhs_dir.glob("*.tape"))

    if not vhs_files:
        print("No VHS tape files found in docs/images/, skipping")
        return

    for vhs_file in vhs_files:
        print(f"Processing: {vhs_file.name}")
        try:
            subprocess.run(
                ["vhs", vhs_file.name],
                check=True,
                cwd=vhs_dir,
            )
            gif_name = vhs_file.stem + ".gif"
            print(f"✓ Generated {gif_name}")
        except FileNotFoundError:
            print(
                "✗ VHS is not installed. Please install it from: "
                "https://github.com/charmbracelet/vhs"
            )
            raise
        except subprocess.CalledProcessError as e:
            print(f"✗ Error processing {vhs_file.name}: {e}")
            raise


if __name__ == "__main__":
    gen_cli_interactive_gifs()
