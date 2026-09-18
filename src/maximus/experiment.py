"""Experiment logging and strict metrics.json contract."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from maximus.competition import Competition


class MetricsError(ValueError):
    """Raised when metrics.json is missing or invalid."""


@dataclass
class ExperimentRecord:
    id: str
    timestamp: str
    metric: float
    metric_name: str
    note: str
    config_hash: str
    dirty: bool
    source: str


def read_metrics(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise MetricsError(f"Missing metrics file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetricsError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise MetricsError(f"{path} must contain a JSON object")
    if "metric" not in data:
        raise MetricsError(f"{path} must include a numeric 'metric' field")
    try:
        metric = float(data["metric"])
    except (TypeError, ValueError) as exc:
        raise MetricsError(f"{path} 'metric' must be a float") from exc
    if metric != metric:  # NaN
        raise MetricsError(f"{path} 'metric' must not be NaN")
    out = dict(data)
    out["metric"] = metric
    return out


def append_experiment(
    competition: Competition,
    *,
    metric: float,
    note: str = "",
    config_hash: str = "",
    dirty: bool = False,
    source: str = "eval",
) -> ExperimentRecord:
    experiments = competition.experiments_dir()
    history_path = experiments / "history.jsonl"
    log_path = experiments / "log.md"

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_id = ts.replace(":", "").replace("-", "")
    record = ExperimentRecord(
        id=run_id,
        timestamp=ts,
        metric=metric,
        metric_name=competition.metric.name,
        note=note.strip(),
        config_hash=config_hash,
        dirty=dirty,
        source=source,
    )

    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record)) + "\n")

    if not log_path.exists():
        log_path.write_text(
            f"# Experiment log — {competition.name}\n\n",
            encoding="utf-8",
        )
    line = (
        f"- `{record.id}` | {competition.metric.name}="
        f"**{record.metric:.6f}** | source={record.source}"
    )
    if record.note:
        line += f" | {record.note}"
    line += "\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)

    return record


def read_history(competition: Competition, limit: int = 20) -> list[dict[str, Any]]:
    path = competition.experiments_dir() / "history.jsonl"
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows[-limit:]


def best_metric(competition: Competition) -> float | None:
    history = read_history(competition, limit=10_000)
    if not history:
        return None
    values = [float(r["metric"]) for r in history]
    if competition.metric.higher_is_better:
        return max(values)
    return min(values)


def append_note(competition: Competition, note: str) -> None:
    experiments = competition.experiments_dir()
    log_path = experiments / "log.md"
    if not log_path.exists():
        log_path.write_text(
            f"# Experiment log — {competition.name}\n\n",
            encoding="utf-8",
        )
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"- note `{ts}` | {note.strip()}\n")


def write_pending_train(competition: Competition, rationale: str, summary: str) -> Path:
    path = competition.experiments_dir() / "pending_train.md"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = (
        f"# Pending train request\n\n"
        f"- requested_at: `{ts}`\n"
        f"- competition: `{competition.name}`\n\n"
        f"## Summary\n\n{summary.strip()}\n\n"
        f"## Rationale\n\n{rationale.strip()}\n\n"
        f"## Approve\n\n"
        f"```bash\nmaximus train --comp {competition.name}\n```\n"
    )
    path.write_text(body, encoding="utf-8")
    return path


def read_experiment_log(competition: Competition, max_chars: int = 8000) -> str:
    path = competition.experiments_dir() / "log.md"
    if not path.is_file():
        return "(no experiment log yet)"
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        return text[-max_chars:]
    return text
