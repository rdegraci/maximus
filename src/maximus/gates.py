"""Train approval gates and run locks."""

from __future__ import annotations

import os
from pathlib import Path

from maximus.competition import Competition


class GateError(RuntimeError):
    """Raised when a gated action is not allowed."""


def train_allowed_via_mcp() -> bool:
    """MCP/agent train is refused unless explicitly enabled."""
    return os.environ.get("MAXIMUS_ALLOW_TRAIN", "").strip() in {
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
    }


def assert_mcp_train_allowed(competition: Competition) -> None:
    if competition.tooling.train_requires_approval and not train_allowed_via_mcp():
        raise GateError(
            "Train is gated. The agent must call request_train and wait. "
            "A human runs `maximus train --comp <name>`. "
            "Set MAXIMUS_ALLOW_TRAIN=1 only if you intentionally override."
        )


def assert_eval_allowed_for_agent(competition: Competition) -> None:
    if not competition.tooling.eval_allowed_for_agent:
        raise GateError(
            f"Eval is not allowed for the agent on competition "
            f"'{competition.name}' (tooling.eval_allowed_for_agent=false)."
        )


class RunLock:
    """Simple file lock so overlapping trains fail loudly."""

    def __init__(self, competition: Competition, name: str = "train") -> None:
        self.path = competition.artifacts_dir() / f".{name}.lock"

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            raise GateError(
                f"Run lock exists at {self.path}. "
                "Another run may be in progress, or a previous run crashed. "
                f"Remove the lock file if it is safe: rm {self.path}"
            )
        self.path.write_text("locked\n", encoding="utf-8")

    def release(self) -> None:
        if self.path.exists():
            self.path.unlink()
