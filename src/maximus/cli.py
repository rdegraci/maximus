"""Maximus CLI."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from maximus import __version__
from maximus import service


def _print(data: Any) -> None:
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2))
    else:
        print(data)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="maximus",
        description="LLM ML-engineer harness for competition workflows",
    )
    p.add_argument("--version", action="version", version=f"maximus {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    new_p = sub.add_parser("new", help="Create a competition from the template")
    new_p.add_argument("name")

    for name, help_text in [
        ("train", "Run training (human-approved compute)"),
        ("eval", "Run evaluation and log metrics"),
        ("submit", "Build a local submission artifact"),
        ("status", "Show best score and recent runs"),
    ]:
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("--comp", "-c", required=True, help="Competition name")

    log_p = sub.add_parser("log", help="Append a note to the experiment log")
    log_p.add_argument("--comp", "-c", required=True)
    log_p.add_argument("--note", required=True)

    sub.add_parser("list", help="List competitions")

    sub.add_parser("mcp", help="Start the Maximus MCP server (stdio)")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.cmd == "new":
            _print(service.new_competition(args.name))
            return 0
        if args.cmd == "list":
            _print(service.list_comps())
            return 0
        if args.cmd == "mcp":
            from maximus.mcp_server import run_mcp

            run_mcp()
            return 0
        if args.cmd == "train":
            result = service.train(args.comp)
            _print(result)
            return 0 if result.get("ok") else 1
        if args.cmd == "eval":
            result = service.eval_competition(args.comp)
            _print(result)
            return 0 if result.get("ok") else 1
        if args.cmd == "submit":
            result = service.submit(args.comp)
            _print(result)
            return 0 if result.get("ok") else 1
        if args.cmd == "status":
            _print(service.status(args.comp))
            return 0
        if args.cmd == "log":
            _print(service.log_note(args.comp, args.note))
            return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
