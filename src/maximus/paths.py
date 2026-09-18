"""Resolve repo and competition paths from a stable root."""

from __future__ import annotations

import os
from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Find the Maximus repo root (directory containing pyproject.toml)."""
    env = os.environ.get("MAXIMUS_ROOT")
    if env:
        root = Path(env).expanduser().resolve()
        if (root / "pyproject.toml").is_file():
            return root
        raise FileNotFoundError(
            f"MAXIMUS_ROOT={root} does not contain pyproject.toml"
        )

    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").is_file():
            name = candidate.name
            # Prefer the maximus project when nested oddly
            if name == "maximus" or (candidate / "src" / "maximus").is_dir():
                return candidate
            if (candidate / "competitions").is_dir():
                return candidate

    # Fallback: package lives in src/maximus → repo is parents[2]
    pkg = Path(__file__).resolve().parent
    repo = pkg.parent.parent
    if (repo / "pyproject.toml").is_file():
        return repo

    raise FileNotFoundError(
        "Could not find Maximus repo root. Run from the repo or set MAXIMUS_ROOT."
    )


def competitions_dir(repo_root: Path | None = None) -> Path:
    return (repo_root or find_repo_root()) / "competitions"


def templates_dir(repo_root: Path | None = None) -> Path:
    return (repo_root or find_repo_root()) / "templates" / "competition"
