"""Evaluate toy_binary model; write artifacts/metrics.json."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.metrics import roc_auc_score


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    artifacts = root / "artifacts"
    model_path = artifacts / "model.joblib"
    split_path = artifacts / "split.joblib"
    if not model_path.is_file():
        raise SystemExit(f"Missing model at {model_path}; run train first")
    if not split_path.is_file():
        raise SystemExit(f"Missing split at {split_path}; run train first")

    model = joblib.load(model_path)
    split = joblib.load(split_path)
    X_test, y_test = split["X_test"], split["y_test"]

    if hasattr(model, "predict_proba"):
        scores = model.predict_proba(X_test)[:, 1]
    else:
        scores = model.decision_function(X_test)

    metric = float(roc_auc_score(y_test, scores))
    metrics = {"metric": metric, "roc_auc": metric}
    (artifacts / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
