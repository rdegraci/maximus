# Bootstrap a competition

You are bootstrapping a Maximus competition baseline.

## Rules

1. Read `competition.yaml` via `get_competition`.
2. Inspect allowed files only (`read_allowed_file`).
3. Create a minimal working train/eval/submit path if missing.
4. Do **not** call train. Use `request_train` when ready for the first run.
5. One coherent baseline — no architecture thrash.

## Goal

A first runnable baseline that writes `artifacts/metrics.json` with a numeric `metric`.
