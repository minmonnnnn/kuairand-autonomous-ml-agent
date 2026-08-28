# Contributing

## 1. Before you touch anything

1. Read `TEAM_SOT.md`.
2. Confirm you own the files you are about to change
   (`docs/coordination/OWNERSHIP_MATRIX.md`).
3. If the change crosses a workstream boundary, open a change request instead
   (`docs/coordination/CHANGE_REQUEST_PROCESS.md`).
4. Make the smallest coherent change. Test it. Record the decision if it matters.

## 2. Branches

```text
main                  protected; integration only, via PR
min/architecture      Min
rishi/features        Rishi
vidush/models         Vidush
sarthak/evaluation    Sarthak
nandit/runtime        Nandit
```

Short-lived topic branches off your workstream branch are fine:
`rishi/features-temporal-buckets`. Do not commit directly to `main`.

## 3. Commits

```text
<area>: <imperative summary>

area ∈ {arch, data, features, models, training, eval, research,
        runtime, monitoring, docs, tests, config, exp}
```

Examples:

```text
features: add within-user impression-rank feature
eval: add seed-variance report to experiment comparison
exp: record EXP-0007 pairwise BPR loss (valid primary 0.6041)
```

If a commit produces a metric, put the number in the body and link the experiment ID.

## 4. Pull requests

Every PR must state:

- which workstream it belongs to
- which files it touches, and confirmation they are owned by you
- whether any interface changed (if yes: change request link)
- what was tested
- status vocabulary for the change: `SCAFFOLDED` / `IMPLEMENTED` / `TESTED` / `VALIDATED`

The PR template enforces this. One approving review from the affected owner is
required; cross-cutting PRs need Min plus each affected owner.

## 5. The rules that are not negotiable

- **Never edit `starter_kit/`.** It is organizer reference code. Adapters go in `src/`.
- **Never reimplement the metrics.** Import `starter_kit/evaluate.py`.
- **Never read the test split during development.** Use `Split.TEST` only in the final
  submission path, and only after the validation-best checkpoint is designated.
- **Never delete a failed experiment.** Move it to `experiments/archived/` at most.
- **Never claim an improvement smaller than 0.0016 Primary** (2σ of seed noise) without
  a multi-seed result and a variance analysis from Sarthak.
- **Never describe scaffolding as implementation** in docs, commits or the SOT.
- **Never commit the dataset**, checkpoints, `.env`, or API keys.

## 6. Status vocabulary

| Status | Means |
|---|---|
| `PLANNED` | Written down, no code |
| `SCAFFOLDED` | Interface/skeleton exists, does not do the job yet |
| `IMPLEMENTED` | Works |
| `TESTED` | Has passing automated tests |
| `VALIDATED` | Verified against the challenge's own criteria (e.g. baseline reproduced) |

## 7. Adding a dependency

Anything on the official-baseline reproduction path stays **NumPy-only**. Other
dependencies go in `requirements.txt` under your workstream's comment block, and get a
one-line justification in the PR.

## 8. Updating the SOT

`TEAM_SOT.md` is owned by Min but **everyone updates their own rows**: your workstream
status, your blockers, your active hypotheses. Update it in the same PR as the change,
not afterwards. Set the "Last updated" line.

## 9. Recording an experiment

Every non-trivial experiment gets an ID and a record. See
`docs/runbooks/EXPERIMENT_RUN.md` and the schema in `src/registry/schema.py`.
Failed and rejected experiments are recorded too.

## 10. Local checks before pushing

```bash
ruff check src tests
pytest -q -m "not requires_data"
```
