"""Run competition shell commands with logging."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from maximus.competition import Competition
from maximus.gates import RunLock


@dataclass
class RunResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    log_path: Path

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def config_hash(competition: Competition) -> str:
    cfg = competition.root / "configs" / "default.yaml"
    if not cfg.is_file():
        return ""
    return hashlib.sha256(cfg.read_bytes()).hexdigest()[:12]


def run_command(
    competition: Competition,
    key: str,
    *,
    use_lock: bool = False,
    lock_name: str = "train",
    timeout: float | None = None,
) -> RunResult:
    command = competition.commands[key]
    artifacts = competition.artifacts_dir()
    artifacts.mkdir(parents=True, exist_ok=True)
    log_path = artifacts / f"last_{key}.log"

    lock = RunLock(competition, lock_name) if use_lock else None
    if lock:
        lock.acquire()

    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(competition.root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        combined = (
            f"$ {command}\n"
            f"cwd: {competition.root}\n"
            f"exit: {proc.returncode}\n\n"
            f"--- stdout ---\n{proc.stdout}\n"
            f"--- stderr ---\n{proc.stderr}\n"
        )
        log_path.write_text(combined, encoding="utf-8")
        meta = {
            "command": command,
            "returncode": proc.returncode,
            "log_path": str(log_path),
        }
        (artifacts / f"last_{key}.json").write_text(
            json.dumps(meta, indent=2) + "\n",
            encoding="utf-8",
        )
        return RunResult(
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            log_path=log_path,
        )
    finally:
        if lock:
            lock.release()


def tail_text(path: Path, max_chars: int = 4000) -> str:
    if not path.is_file():
        return f"(missing {path})"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[-max_chars:]
    return text
