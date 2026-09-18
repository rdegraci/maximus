"""Load and validate competition.yaml contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from maximus.paths import competitions_dir, find_repo_root


@dataclass
class MetricSpec:
    name: str
    higher_is_better: bool = True


@dataclass
class ToolingSpec:
    eval_allowed_for_agent: bool = True
    train_requires_approval: bool = True


@dataclass
class Competition:
    name: str
    root: Path
    task: str
    metric: MetricSpec
    commands: dict[str, str]
    allowed_edit_globs: list[str]
    paths: dict[str, str]
    tooling: ToolingSpec = field(default_factory=ToolingSpec)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def resolve(self, key: str) -> Path:
        rel = self.paths.get(key)
        if not rel:
            raise KeyError(f"Unknown path key: {key}")
        return (self.root / rel).resolve()

    def artifacts_dir(self) -> Path:
        return self.resolve("artifacts")

    def metrics_path(self) -> Path:
        return self.artifacts_dir() / "metrics.json"

    def experiments_dir(self) -> Path:
        d = self.root / "experiments"
        d.mkdir(parents=True, exist_ok=True)
        return d


def _require(data: dict[str, Any], key: str) -> Any:
    if key not in data:
        raise ValueError(f"competition.yaml missing required key: {key}")
    return data[key]


def load_competition(name: str, repo_root: Path | None = None) -> Competition:
    root = find_repo_root(repo_root) if repo_root is None else repo_root
    comp_root = competitions_dir(root) / name
    yaml_path = comp_root / "competition.yaml"
    if not yaml_path.is_file():
        raise FileNotFoundError(f"No competition.yaml at {yaml_path}")

    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("competition.yaml must be a mapping")

    metric_raw = _require(data, "metric")
    if isinstance(metric_raw, str):
        metric = MetricSpec(name=metric_raw, higher_is_better=True)
    else:
        metric = MetricSpec(
            name=str(_require(metric_raw, "name")),
            higher_is_better=bool(metric_raw.get("higher_is_better", True)),
        )

    tooling_raw = data.get("tooling") or {}
    tooling = ToolingSpec(
        eval_allowed_for_agent=bool(
            tooling_raw.get("eval_allowed_for_agent", True)
        ),
        train_requires_approval=bool(
            tooling_raw.get("train_requires_approval", True)
        ),
    )

    commands = _require(data, "commands")
    if not isinstance(commands, dict):
        raise ValueError("commands must be a mapping")
    for required in ("train", "eval", "submit"):
        if required not in commands:
            raise ValueError(f"commands.{required} is required")

    paths = data.get("paths") or {
        "data": "data",
        "artifacts": "artifacts",
        "submission": "artifacts/submission.csv",
    }

    return Competition(
        name=str(data.get("name") or name),
        root=comp_root.resolve(),
        task=str(data.get("task") or ""),
        metric=metric,
        commands={str(k): str(v) for k, v in commands.items()},
        allowed_edit_globs=[
            str(g) for g in (data.get("allowed_edit_globs") or ["src/**", "configs/**"])
        ],
        paths={str(k): str(v) for k, v in paths.items()},
        tooling=tooling,
        raw=data,
    )


def list_competition_names(repo_root: Path | None = None) -> list[str]:
    root = find_repo_root() if repo_root is None else repo_root
    base = competitions_dir(root)
    if not base.is_dir():
        return []
    names = []
    for child in sorted(base.iterdir()):
        if child.is_dir() and (child / "competition.yaml").is_file():
            names.append(child.name)
    return names
