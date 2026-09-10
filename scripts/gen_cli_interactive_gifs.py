"""Render docs/images/*.tape with VHS in parallel.

Usage:
    uv run poe doc:screenshots                        # default (parallel)
    python scripts/gen_cli_interactive_gifs.py        # default (parallel)
    python scripts/gen_cli_interactive_gifs.py -j 1   # serial
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

VHS_DIR = Path(__file__).parent.parent / "docs" / "images"
OUTPUT_DIR = VHS_DIR / "cli_interactive"


def gen_cli_interactive_gifs(max_workers: int | None = None) -> None:
    """Render every ``docs/images/*.tape`` with VHS in parallel.

    ``max_workers`` defaults to ``min(len(tapes), 4)``; pass ``1`` for serial.
    """
    if shutil.which("vhs") is None:
        raise SystemExit(
            "VHS is not installed. Please install it from: "
            "https://github.com/charmbracelet/vhs"
        )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tapes = sorted(VHS_DIR.glob("*.tape"))
    if not tapes:
        print("No VHS tape files found in docs/images/, skipping")
        return

    workers = max(1, max_workers if max_workers is not None else min(len(tapes), 4))
    print(f"Rendering {len(tapes)} tape(s) with up to {workers} worker(s)")

    def _render(tape: Path) -> None:
        subprocess.run(
            ["vhs", tape.name],
            check=True,
            cwd=VHS_DIR,
            capture_output=True,
            text=True,
        )

    errors: list[Path] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_render, t): t for t in tapes}
        for fut in as_completed(futures):
            tape = futures[fut]
            try:
                fut.result()
            except subprocess.CalledProcessError as exc:
                print(f"✗ {tape.name}", file=sys.stderr)
                if exc.stdout:
                    print(exc.stdout, file=sys.stderr)
                if exc.stderr:
                    print(exc.stderr, file=sys.stderr)
                errors.append(tape)
            else:
                print(f"✓ {tape.stem}.gif")

    if errors:
        raise SystemExit("vhs failed for: " + ", ".join(t.name for t in errors))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "-j",
        "--max-workers",
        type=int,
        default=None,
        help="Max parallel vhs invocations. Default: min(len(tapes), 4). Use 1 for serial.",
    )
    args = parser.parse_args()
    gen_cli_interactive_gifs(args.max_workers)
