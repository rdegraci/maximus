# Quick Start

Get Maximus running on the built-in `toy_binary` competition in a few minutes.

## Install

From the repo root:

```bash
pip install -e .
```

Confirm:

```bash
maximus --version
maximus list
```

## First loop

```bash
maximus train --comp toy_binary
maximus eval --comp toy_binary
maximus status --comp toy_binary
```

You should see a ROC-AUC metric in the status output and a new line in
`competitions/toy_binary/experiments/log.md`.

Optional local submission artifact:

```bash
maximus submit --comp toy_binary
```

## One improve cycle (with an agent)

1. Ask the Cursor agent to improve `toy_binary` (Maximus skill + MCP tools).
2. The agent edits one allowed file and calls `request_train`.
3. You approve compute:

```bash
maximus train --comp toy_binary
```

4. Tell the agent training finished; it runs eval/status via tools.

See [Operator Guide](OPERATOR-GUIDE.md) for CLI/MCP details and guardrails.
