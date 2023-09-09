from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def chdir(tmp_path: Path) -> Iterator[Path]:
    cwd = Path()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)
