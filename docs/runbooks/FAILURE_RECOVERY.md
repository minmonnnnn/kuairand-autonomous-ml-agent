# Runbook · Failure Recovery

Owner: Nandit · Status: `PLANNED` (see tasks `T-504`, `T-505`)

## Principle

The goal is not zero failures. The goal is **robust recovery** — the agent keeps making
progress when things break. A run that dies on iteration 4 of 50 because of an
unhandled exception scores worse than one that hits 12 failures and recovers from
all of them.

## Failure taxonomy and default response

| Failure | Detection | Default action |
|---|---|---|
| Invalid configuration | schema validation before launch | `SKIP` — mark the spec invalid, select a different experiment |
| Missing data file | pre-flight path check | `ESCALATE` — cannot be fixed autonomously |
| Malformed data row | loader raises | `RETRY_WITH_PATCH` — quarantine the row, log it, continue |
| Training crash | non-zero subprocess exit | `RETRY` once, then `ROLLBACK` |
| Timeout | wall-clock exceeds `timeout_seconds` | `ROLLBACK` to last good checkpoint, reduce scope, requeue |
| NaN / Inf loss | per-batch finite check | `RETRY_WITH_PATCH` — lower LR or clip gradients, once |
| Non-finite scores | validation before evaluation | `INVALID_OUTPUT`, no metrics recorded, `RETRY` |
| Invalid checkpoint | load fails or shape mismatch | `ROLLBACK` |
| Invalid submission | `submit.py --check` fails | `RETRY` regeneration; if it fails twice, `ESCALATE` |
| Subprocess killed (OOM) | exit signal | `RETRY` with reduced batch size, then `SKIP` |

## The escalation budget

`ESCALATE` increments `manual_interventions`, which is a **graded** metric — autonomy is
20% of the score. Treat every escalation as a cost. Before adding one, ask whether the
agent could instead skip the experiment and continue, which preserves autonomy at the
cost of one iteration.

Escalation is correct when continuing would corrupt results (missing data, a broken
evaluator). It is not correct merely because a single experiment failed.

## Rollback semantics

A rollback restores three things together: the last known-good **checkpoint**, its
**git commit**, and its **resolved config**. Restoring one without the others produces
an unreproducible state, which is worse than the failure.

## Recording

Every failure, retry and recovery action lands in the iteration log and in the
experiment record's `errors` and `recovery_actions` fields. Never swallow an exception.
Never delete a failed run's directory — move it to `runs/failed/`.

## Testing recovery

`tests/reliability/` should inject each row of the taxonomy above and assert the correct
action was taken. The recovery path is the part most likely to be broken precisely
because it only runs when something else already went wrong.
