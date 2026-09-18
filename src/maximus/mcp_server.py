"""Maximus MCP server — agent tools for grunt work; train is gated."""

from __future__ import annotations

import json
from typing import Any

from maximus import service
from maximus.experiment import read_experiment_log
from maximus.gates import GateError


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def run_mcp() -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("maximus")

    @mcp.tool()
    def list_competitions() -> str:
        """List available competition folder names."""
        return _json(service.list_comps())

    @mcp.tool()
    def get_competition(comp: str) -> str:
        """Read the competition.yaml contract and a short experiment log tail."""
        return _json(service.competition_summary(comp))

    @mcp.tool()
    def status(comp: str, limit: int = 10) -> str:
        """Show best score and recent experiment history."""
        return _json(service.status(comp, limit=limit))

    @mcp.tool()
    def read_experiment_log_tool(comp: str) -> str:
        """Read the competition experiment markdown log."""
        c = service.get_competition(comp)
        return read_experiment_log(c)

    @mcp.tool()
    def read_metrics(comp: str) -> str:
        """Read artifacts/metrics.json (strict schema)."""
        return _json(service.read_metrics_tool(comp))

    @mcp.tool()
    def read_allowed_file(comp: str, path: str) -> str:
        """Read a file under allowed_edit_globs (relative to competition root)."""
        return _json(service.read_allowed_file(comp, path))

    @mcp.tool()
    def write_allowed_file(comp: str, path: str, content: str) -> str:
        """Write a file under allowed_edit_globs (relative to competition root)."""
        return _json(service.write_allowed_file(comp, path, content))

    @mcp.tool()
    def run_eval(comp: str, note: str = "") -> str:
        """Run eval and append metrics to the experiment log (if allowed for agent)."""
        try:
            return _json(service.mcp_eval(comp, note=note))
        except GateError as exc:
            return _json({"ok": False, "error": str(exc)})

    @mcp.tool()
    def prepare_submit(comp: str) -> str:
        """Build a local submission artifact (no contest-site upload)."""
        return _json(service.submit(comp))

    @mcp.tool()
    def diagnose_last_run(comp: str, kind: str = "train") -> str:
        """Tail logs from the last train, eval, or submit run."""
        return _json(service.diagnose_last_run(comp, kind=kind))

    @mcp.tool()
    def request_train(comp: str, rationale: str, summary: str) -> str:
        """Record a train proposal. Does NOT start training. Stop and wait for human approval."""
        return _json(
            service.request_train(comp, rationale=rationale, summary=summary)
        )

    @mcp.tool()
    def train(comp: str) -> str:
        """Refused unless MAXIMUS_ALLOW_TRAIN=1. Prefer request_train + human CLI."""
        try:
            return _json(service.mcp_train(comp))
        except GateError as exc:
            return _json({"ok": False, "error": str(exc)})

    mcp.run(transport="stdio")
