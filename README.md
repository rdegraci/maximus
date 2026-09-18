# Maximus

LLM ML-engineer harness for competition workflows.

Maximus wraps an agent in a fixed **propose → (you approve train) → eval → log → improve** loop so you can iterate on contest models without pasting logs by hand — and without letting the agent burn compute unsupervised.

- **[Quick Start](docs/QUICK-START.md)** — install and run `toy_binary` in minutes
- **[Operator Guide](docs/OPERATOR-GUIDE.md)** — CLI, MCP tools, train gate, troubleshooting

## What it is

- A **CLI** for train / eval / submit / status
- An **MCP server** so a Cursor agent can do grunt work (status, logs, scoped edits, eval, submit prep)
- A **gated train** path: the agent may only `request_train`; you run `maximus train`
- An **experiment log** with a strict `metrics.json` contract
- A **toy competition** (`toy_binary`) to prove the loop on CPU

## What it is not

- Not AutoML that trains in a loop unsupervised
- Not a DrivenData/Kaggle uploader
- Not a GEMS/geophysics solution (add real contests later as new folders)

## Features

| Feature | Notes |
|---------|--------|
| CLI | `maximus train\|eval\|submit\|status\|log\|new\|mcp` |
| MCP tools | Status, logs, scoped file I/O, eval, submit prep, `request_train` |
| Train gate | MCP `train` refused unless `MAXIMUS_ALLOW_TRAIN=1` |
| Experiment log | `experiments/log.md` + `history.jsonl` |
| Template | `maximus new <name>` |
| Toy demo | Logistic regression / optional random forest, ROC-AUC |

## Requirements

- Python 3.10+
- macOS/Linux recommended

## Install

```bash
cd /path/to/maximus
pip install -e .
```

## Quickstart

```bash
maximus train --comp toy_binary
maximus eval --comp toy_binary
maximus status --comp toy_binary
```

Full steps: [docs/QUICK-START.md](docs/QUICK-START.md).

## CLI / MCP overview

Human path (includes train):

```bash
maximus train --comp toy_binary
maximus eval --comp toy_binary
maximus status --comp toy_binary
```

Agent path: connect Cursor to `maximus mcp`, then use tools for status/edits/`request_train`/`run_eval`. Details: [docs/OPERATOR-GUIDE.md](docs/OPERATOR-GUIDE.md).

## Project structure

```text
maximus/
  src/maximus/           # CLI + MCP + shared services
  competitions/          # One folder per contest
    toy_binary/
  templates/competition/ # Scaffold for maximus new
  prompts/               # Improve / bootstrap / diagnose
  docs/                  # Quick Start + Operator Guide
  .cursor/skills/        # Agent skill for this repo
```

## Roadmap (after MVP)

- Add real contests as `competitions/<name>` (e.g. GEMS) once the toy loop feels boring
- Optional heavier eval gating per competition
- No autonomous multi-train loops in the default path

## License

MIT — see [LICENSE](LICENSE). Copyright 2026 Rodney Degracia.
