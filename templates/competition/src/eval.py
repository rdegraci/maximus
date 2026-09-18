"""Eval stub — replace for your competition."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    metrics = {"metric": 0.0}
    (artifacts / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
