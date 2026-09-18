"""Submit stub — replace for your competition."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    out = artifacts / "submission.csv"
    out.write_text("id,prediction\n0,0\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
