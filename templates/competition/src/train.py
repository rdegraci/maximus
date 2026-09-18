"""Train stub — replace for your competition."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "model.txt").write_text("stub\n", encoding="utf-8")
    print("stub train complete")


if __name__ == "__main__":
    main()
