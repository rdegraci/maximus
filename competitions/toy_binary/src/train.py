"""Train a simple classifier for toy_binary."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.dataset import load_split


def load_config(root: Path) -> dict:
    path = root / "configs" / "default.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_model(cfg: dict):
    name = str(cfg.get("model", "logistic_regression"))
    if name == "logistic_regression":
        clf = LogisticRegression(
            C=float(cfg.get("C", 1.0)),
            max_iter=int(cfg.get("max_iter", 200)),
            random_state=int(cfg.get("seed", 42)),
        )
        return Pipeline([("scaler", StandardScaler()), ("clf", clf)])
    if name == "random_forest":
        return RandomForestClassifier(
            n_estimators=int(cfg.get("n_estimators", 100)),
            max_depth=cfg.get("max_depth"),
            random_state=int(cfg.get("seed", 42)),
        )
    raise ValueError(f"Unknown model: {name}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_config(root)
    split = load_split(
        n_samples=int(cfg["n_samples"]),
        n_features=int(cfg["n_features"]),
        test_size=float(cfg["test_size"]),
        seed=int(cfg["seed"]),
    )
    model = build_model(cfg)
    model.fit(split.X_train, split.y_train)

    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    model_path = artifacts / "model.joblib"
    joblib.dump(model, model_path)

    meta = {
        "model": cfg.get("model"),
        "n_train": int(split.X_train.shape[0]),
        "n_test": int(split.X_test.shape[0]),
        "config": cfg,
    }
    (artifacts / "train_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n",
        encoding="utf-8",
    )
    # Persist test split for eval reproducibility
    joblib.dump(
        {
            "X_test": split.X_test,
            "y_test": split.y_test,
            "X_train": split.X_train,
            "y_train": split.y_train,
        },
        artifacts / "split.joblib",
    )
    print(f"wrote {model_path}")


if __name__ == "__main__":
    main()
