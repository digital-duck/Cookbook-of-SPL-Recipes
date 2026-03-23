"""
spl_cookbook.cli — Entry points for spl-cookbook console scripts.

Commands
--------
recipe-kitchen   Launch the Streamlit browser UI (Playground + Recipe Maker + Bake-All)
bake-all         Run all active recipes from the CLI without the UI
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _find_kitchen_app() -> Path:
    """Locate recipe_kitchen.py whether running from repo or installed package."""
    # 1. Explicit override
    if "SPL_KITCHEN_APP" in os.environ:
        return Path(os.environ["SPL_KITCHEN_APP"])

    # 2. Installed package: kitchen app lives next to this module
    pkg_dir = Path(__file__).resolve().parent
    bundled = pkg_dir / "_kitchen.py"
    if bundled.exists():
        return bundled

    # 3. Development / editable install: walk up to repo root → scripts/
    here = pkg_dir
    for _ in range(5):
        candidate = here / "scripts" / "recipe_kitchen.py"
        if candidate.exists():
            return candidate
        here = here.parent

    raise FileNotFoundError(
        "recipe_kitchen.py not found. "
        "Set SPL_KITCHEN_APP=/path/to/recipe_kitchen.py to override."
    )


def _find_run_all() -> Path:
    """Locate run_all.py relative to the cookbook."""
    if "SPL_COOKBOOK_DIR" in os.environ:
        p = Path(os.environ["SPL_COOKBOOK_DIR"]) / "run_all.py"
        if p.exists():
            return p

    here = Path(__file__).resolve().parent
    for _ in range(6):
        candidate = here / "references" / "SPL20" / "cookbook" / "run_all.py"
        if candidate.exists():
            return candidate
        here = here.parent

    raise FileNotFoundError(
        "run_all.py not found. "
        "Set SPL_COOKBOOK_DIR=/path/to/cookbook to override."
    )


def recipe_kitchen() -> None:
    """Launch the SPL Recipe Kitchen Streamlit UI."""
    app = _find_kitchen_app()
    # Pass through any extra args (e.g. --server.port 8502)
    cmd = ["streamlit", "run", str(app)] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))


def bake_all() -> None:
    """Run all active cookbook recipes from the command line."""
    run_all = _find_run_all()
    cmd = [sys.executable, str(run_all)] + sys.argv[1:]
    sys.exit(subprocess.call(cmd, cwd=str(run_all.parent.parent)))
