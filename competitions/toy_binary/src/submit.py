"""Build a local submission CSV for toy_binary."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    artifacts = root / "artifacts"
    model = joblib.load(artifacts / "model.joblib")
    split = joblib.load(artifacts / "split.joblib")
    X_test = split["X_test"]
    if hasattr(model, "predict_proba"):
        preds = model.predict_proba(X_test)[:, 1]
    else:
        preds = model.decision_function(X_test)

    out = artifacts / "submission.csv"
    lines = ["id,prediction"]
    for i, p in enumerate(np.asarray(preds).tolist()):
        lines.append(f"{i},{p:.8f}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
