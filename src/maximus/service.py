"""High-level operations shared by CLI and MCP."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from maximus.competition import Competition, list_competition_names, load_competition
from maximus.experiment import (
    MetricsError,
    append_experiment,
    append_note,
    best_metric,
    read_experiment_log,
    read_history,
    read_metrics,
    write_pending_train,
)
from maximus.gates import (
    GateError,
    assert_eval_allowed_for_agent,
    assert_mcp_train_allowed,
)
from maximus.paths import find_repo_root, templates_dir
from maximus.runner import config_hash, run_command, tail_text


def get_competition(name: str) -> Competition:
    return load_competition(name)


def status(name: str, limit: int = 10) -> dict[str, Any]:
    comp = load_competition(name)
    history = read_history(comp, limit=limit)
    best = best_metric(comp)
    pending = comp.experiments_dir() / "pending_train.md"
    return {
        "competition": comp.name,
        "metric_name": comp.metric.name,
        "higher_is_better": comp.metric.higher_is_better,
        "best_metric": best,
        "recent": history,
        "pending_train": pending.is_file(),
        "pending_train_path": str(pending) if pending.is_file() else None,
        "root": str(comp.root),
    }


def train(name: str) -> dict[str, Any]:
    comp = load_competition(name)
    result = run_command(comp, "train", use_lock=True, lock_name="train")
    return {
        "ok": result.ok,
        "returncode": result.returncode,
        "log_path": str(result.log_path),
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
        "config_hash": config_hash(comp),
    }


def eval_competition(name: str, *, note: str = "", source: str = "eval") -> dict[str, Any]:
    comp = load_competition(name)
    result = run_command(comp, "eval", use_lock=False)
    if not result.ok:
        return {
            "ok": False,
            "returncode": result.returncode,
            "log_path": str(result.log_path),
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
            "error": "eval command failed",
        }
    try:
        metrics = read_metrics(comp.metrics_path())
    except MetricsError as exc:
        return {
            "ok": False,
            "returncode": result.returncode,
            "log_path": str(result.log_path),
            "error": str(exc),
        }
    record = append_experiment(
        comp,
        metric=float(metrics["metric"]),
        note=note,
        config_hash=config_hash(comp),
        source=source,
    )
    return {
        "ok": True,
        "metric": record.metric,
        "metric_name": record.metric_name,
        "record_id": record.id,
        "metrics": metrics,
        "log_path": str(result.log_path),
        "best_metric": best_metric(comp),
    }


def submit(name: str) -> dict[str, Any]:
    comp = load_competition(name)
    result = run_command(comp, "submit", use_lock=False)
    return {
        "ok": result.ok,
        "returncode": result.returncode,
        "log_path": str(result.log_path),
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
        "submission_path": str(comp.resolve("submission")),
    }


def log_note(name: str, note: str) -> dict[str, Any]:
    comp = load_competition(name)
    append_note(comp, note)
    return {"ok": True, "competition": name}


def request_train(name: str, rationale: str, summary: str) -> dict[str, Any]:
    comp = load_competition(name)
    path = write_pending_train(comp, rationale=rationale, summary=summary)
    return {
        "ok": True,
        "pending_path": str(path),
        "message": (
            "Train request recorded. A human must run: "
            f"maximus train --comp {name}"
        ),
        "approve_command": f"maximus train --comp {name}",
    }


def mcp_train(name: str) -> dict[str, Any]:
    comp = load_competition(name)
    assert_mcp_train_allowed(comp)
    return train(name)


def mcp_eval(name: str, note: str = "") -> dict[str, Any]:
    comp = load_competition(name)
    assert_eval_allowed_for_agent(comp)
    return eval_competition(name, note=note, source="agent_eval")


def diagnose_last_run(name: str, kind: str = "train") -> dict[str, Any]:
    comp = load_competition(name)
    if kind not in {"train", "eval", "submit"}:
        raise ValueError("kind must be train, eval, or submit")
    log_path = comp.artifacts_dir() / f"last_{kind}.log"
    meta_path = comp.artifacts_dir() / f"last_{kind}.json"
    meta: dict[str, Any] = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return {
        "kind": kind,
        "meta": meta,
        "log_tail": tail_text(log_path),
        "log_path": str(log_path),
    }


def read_metrics_tool(name: str) -> dict[str, Any]:
    comp = load_competition(name)
    return read_metrics(comp.metrics_path())


def allowed_path(competition: Competition, rel_path: str) -> Path:
    """Resolve a relative path and ensure it is under allowed_edit_globs."""
    from fnmatch import fnmatch

    rel = Path(rel_path)
    if rel.is_absolute():
        raise GateError("Path must be relative to the competition root")
    target = (competition.root / rel).resolve()
    try:
        target.relative_to(competition.root.resolve())
    except ValueError as exc:
        raise GateError("Path escapes competition root") from exc

    rel_posix = target.relative_to(competition.root.resolve()).as_posix()
    for pattern in competition.allowed_edit_globs:
        # Support both path and ** globs
        if fnmatch(rel_posix, pattern) or fnmatch(rel_posix, pattern.rstrip("/")):
            return target
        # Also allow matching directories prefixes like configs/**
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            if rel_posix == prefix or rel_posix.startswith(prefix + "/"):
                return target
    raise GateError(
        f"{rel_posix} is outside allowed_edit_globs: "
        f"{competition.allowed_edit_globs}"
    )


def read_allowed_file(name: str, rel_path: str) -> dict[str, Any]:
    comp = load_competition(name)
    path = allowed_path(comp, rel_path)
    if not path.is_file():
        raise FileNotFoundError(f"Not a file: {rel_path}")
    return {"path": rel_path, "content": path.read_text(encoding="utf-8")}


def write_allowed_file(name: str, rel_path: str, content: str) -> dict[str, Any]:
    comp = load_competition(name)
    path = allowed_path(comp, rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"ok": True, "path": rel_path, "bytes": len(content.encode("utf-8"))}


def new_competition(name: str) -> dict[str, Any]:
    if not name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Competition name must be alphanumeric/underscore/hyphen")
    repo = find_repo_root()
    dest = repo / "competitions" / name
    if dest.exists():
        raise FileExistsError(f"Competition already exists: {dest}")
    src = templates_dir(repo)
    if not src.is_dir():
        raise FileNotFoundError(f"Missing template at {src}")
    shutil.copytree(src, dest)
    # Rewrite name in competition.yaml if present
    yaml_path = dest / "competition.yaml"
    if yaml_path.is_file():
        text = yaml_path.read_text(encoding="utf-8")
        text = text.replace("name: template", f"name: {name}", 1)
        text = text.replace("name: toy_binary", f"name: {name}", 1)
        yaml_path.write_text(text, encoding="utf-8")
    return {"ok": True, "path": str(dest)}


def competition_summary(name: str) -> dict[str, Any]:
    comp = load_competition(name)
    return {
        "name": comp.name,
        "task": comp.task,
        "metric": {
            "name": comp.metric.name,
            "higher_is_better": comp.metric.higher_is_better,
        },
        "commands": comp.commands,
        "allowed_edit_globs": comp.allowed_edit_globs,
        "paths": comp.paths,
        "tooling": {
            "eval_allowed_for_agent": comp.tooling.eval_allowed_for_agent,
            "train_requires_approval": comp.tooling.train_requires_approval,
        },
        "root": str(comp.root),
        "experiment_log": read_experiment_log(comp, max_chars=2000),
    }


def list_comps() -> list[str]:
    return list_competition_names()
