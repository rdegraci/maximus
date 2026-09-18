# Operator Guide

How to operate Maximus as the human in the loop.

## Concepts

- **Competition folder** — `competitions/<name>/` with `competition.yaml`, code, configs, artifacts, experiments.
- **CLI** — you can run anything, including `train`.
- **MCP tools** — the agent automates grunt work; **train is gated**.
- **Experiment log** — every successful eval appends to `experiments/history.jsonl` and `experiments/log.md`.

## Repo root contract

Run Maximus from the repository root (the directory with `pyproject.toml`), or set:

```bash
export MAXIMUS_ROOT=/path/to/maximus
```

Tools resolve competitions from that root. Wrong cwd is a common failure mode.

## CLI reference

| Command | Purpose |
|---------|---------|
| `maximus list` | List competitions |
| `maximus new <name>` | Copy `templates/competition` → `competitions/<name>` |
| `maximus train --comp <name>` | Run training (human path) |
| `maximus eval --comp <name>` | Run eval; require `artifacts/metrics.json` with numeric `metric` |
| `maximus submit --comp <name>` | Build local submission artifact |
| `maximus status --comp <name>` | Best score + recent runs |
| `maximus log --comp <name> --note "..."` | Append a manual note |
| `maximus mcp` | Start MCP server on stdio |

## Metrics contract

After eval, `artifacts/metrics.json` must look like:

```json
{
  "metric": 0.84
}
```

`metric` must be a finite float. Extra fields are allowed. Soft/partial parses are rejected.

## Train approval ritual

1. Agent inspects status/logs and makes **one** change.
2. Agent calls MCP `request_train` → writes `experiments/pending_train.md`.
3. You review the proposal, then run:

```bash
maximus train --comp <name>
```

4. Agent calls `run_eval` / `status` (does not need you to paste metrics).

The MCP `train` tool refuses unless `MAXIMUS_ALLOW_TRAIN=1`. Prefer the ritual above.

## MCP setup (Cursor)

1. Install the package (`pip install -e .`) so `maximus` is on your PATH.
2. Add an MCP server that runs `maximus mcp` (stdio) from the repo root.
3. Restart MCP / Cursor so tools appear.

### Agent-facing tools

| Tool | Purpose |
|------|---------|
| `list_competitions` | Discover contests |
| `get_competition` | Contract + short log |
| `status` | Best + recent runs |
| `read_experiment_log_tool` | Markdown log |
| `read_metrics` | Latest metrics.json |
| `read_allowed_file` / `write_allowed_file` | Scoped edits |
| `run_eval` | Eval + log (if allowed) |
| `prepare_submit` | Local submission only |
| `diagnose_last_run` | Tail last run logs |
| `request_train` | Proposal only — does not train |
| `train` | Gated; normally refused |

Per-competition: set `tooling.eval_allowed_for_agent: false` in `competition.yaml` if eval is expensive.

## Adding a competition

```bash
maximus new my_contest
```

Then implement `src/train.py`, `src/eval.py`, `src/submit.py`, and edit `competition.yaml` (commands, metric, allowed globs, paths).

## Guardrails

- Agent: one change per cycle; no auto-train loops.
- Agent: only edit `allowed_edit_globs`.
- Human: owns `train` and any cloud spend.
- No contest-site upload in Maximus MVP.

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| `Could not find Maximus repo root` | `cd` to repo or set `MAXIMUS_ROOT` |
| `Missing metrics file` | Ensure eval writes `artifacts/metrics.json` |
| `Run lock exists` | Another run in progress, or crash; remove `artifacts/.train.lock` if safe |
| MCP tools missing | Confirm `maximus mcp` works; check Cursor MCP config and PATH |
| `Train is gated` on MCP | Expected — use `request_train` + CLI train |
| Import errors in toy_binary | Run commands via `maximus` so cwd is the competition root |

## Prompt pack

- `prompts/improve.md`
- `prompts/bootstrap.md`
- `prompts/diagnose.md`

Project skill: `.cursor/skills/maximus-ml-engineer/SKILL.md`
