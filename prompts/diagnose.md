# Diagnose a failed run

A Maximus train or eval failed.

## Steps

1. `diagnose_last_run` for `train` and/or `eval`
2. `read_metrics` only if eval claimed success
3. Identify the root cause from logs
4. Make **one** fix within `allowed_edit_globs`
5. `request_train` if retraining is required; otherwise tell the human to re-run eval
6. Do not auto-train
