# TEAM SOURCE OF TRUTH

> **Read this before making any change.** This document holds **current state only**.
> History belongs in `experiments/`, `docs/decisions/DECISIONS.md`, and `logs/`.
>
> Last updated: `2026-08-28` · Updated by: `Min` · Repo status: **MILESTONE 0**

---

## 1. Current objective

Complete Milestone 0 (repository foundation) and Milestone 1 (reproduce the official
FM baseline and record it as `EXP-0000-OFFICIAL-BASELINE`). No optimisation work should
begin before Milestone 1 passes.

## 2. Challenge constraints

- Required benchmark: **KuaiRand-Pure**. Determines 100% of the Primary metric.
- Allowed: open-source libraries, papers, public solutions, pretrained weights.
- Prohibited: external training data, augmenting with another dataset, pretrained
  weights trained on hidden-test labels, hidden-test access during development.
- Run limits: 50 iterations or 6 hours wall-clock, whichever comes first.

## 3. Official baseline (organizer-provided, not ours)

FM, `k=16`, `lr=0.001`, batch 8192, max 40 epochs, patience 4, 5 categorical fields,
NumPy only, ~40s on one CPU core.

| Split | GAUC | nDCG@5 | Primary |
|---|---:|---:|---:|
| valid | 0.6674 | 0.5357 | 0.6016 |
| test | 0.6610 | 0.5282 | 0.5946 |

Seed std (5 seeds, test): 0.0008 on all three metrics.

Reference rungs — random Primary `0.4753`, item popularity Primary `0.5715`,
oracle ceiling Primary `0.8645` (test) / `0.8484` (valid).

## 4. Dataset splits

| Split | Dates | Rows | Access |
|---|---|---:|---|
| train | 20220408–20220421 | 1,141,112 | DEVELOPMENT |
| valid | 20220422–20220428 | 124,909 | VALIDATION |
| test | 20220429–20220508 | 170,588 | **FINAL-ONLY** |

## 5. Evaluation definitions

`Primary = mean(GAUC, nDCG@5)`. Authoritative implementation: `starter_kit/evaluate.py`.

- Users with zero positives get nDCG = 0 and **remain** in the average.
- GAUC counts only users with `0 < positives < impressions`, weighted by positive count.
- nDCG gain is `2^rel - 1`.

Never implement a competing metric definition.

## 6. Current validation-best result

**None.** No experiment has been run.

| Field | Value |
|---|---|
| Best experiment | — |
| Validation GAUC | — |
| Validation nDCG@5 | — |
| Validation Primary | — |
| Delta vs official baseline | — |
| Checkpoint | — |
| Git commit | — |

## 7. Current iteration

`0` — no autonomous run has been started.

## 8. Convergence status

`NOT_STARTED`. Terminal states are `CONVERGED` / `MAX_ITERATIONS` / `TIMEOUT`.

## 9. Team ownership

| Person | Workstream | Branch |
|---|---|---|
| Min | Architecture, orchestration, integration | `min/architecture` |
| Rishi | Data & features | `rishi/features` |
| Vidush | Models & training | `vidush/models` |
| Sarthak | Evaluation, experimental science, research | `sarthak/evaluation` |
| Nandit | Runtime, robustness, recovery, resources | `nandit/runtime` |

## 10. Active workstreams

All five are at Milestone 0 → Milestone 1 setup. See
`docs/coordination/TASK_BOARD.md` for per-person tasks.

## 11. Completed workstreams

- Repository foundation scaffolded (Min) — `SCAFFOLDED`

## 12. Blocked workstreams

None. Note that all workstreams need the dataset downloaded locally
(`docs/runbooks/LOCAL_SETUP.md`) before producing numbers.

## 13. Interface contracts

Defined in `docs/coordination/INTERFACE_CONTRACTS.md`. All at version `v0` (scaffolded).
Changing a contract requires a change request.

## 14. Current decisions

See `docs/decisions/DECISIONS.md`. Key standing decisions:

- `D-001` Starter kit is preserved verbatim; all adaptation happens in `src/`.
- `D-002` `starter_kit/evaluate.py` is the single source of metric truth.
- `D-003` Ownership is enforced by directory and by CODEOWNERS, not by convention.
- `D-004` Statistical significance floor is 2σ = 0.0016 Primary.

## 15. Active hypotheses

`H-001` (loss function alignment) is drafted as the template example and sits at the
top of `research/hypothesis_queue/`. Nothing has been tested.

## 16. Rejected approaches

Rejected on **organizer-published evidence**, before we ran anything:

| Approach | Evidence |
|---|---|
| Adding static categorical features (CWM's 13 fields) | Primary 0.5940 vs 0.5950 — inside noise |
| Increasing embedding dimension (k = 8/16/32) | 0.5895 / 0.5902 / 0.5887 — flat |
| Pure user-side first-order features | Mathematically zero effect on within-user order |

Re-testing these requires a documented reason in `research/rejected/`.

## 17. Known issues

- `KI-001` The hidden test labels are physically present in the downloaded dataset.
  The "hidden" test is therefore **self-policed**. Enforcement is procedural
  (`docs/runbooks/DATA_LEAKAGE_POLICY.md`) plus a guarded data loader in `src/data/`.
- `KI-002` No CI runs the baseline (needs the dataset, which is not committed).
  Baseline reproduction is a local, manually-recorded step for now.

## 18. Manual interventions

`0` recorded. Counter lives in `logs/resources/`.

## 19. Resource usage

| Metric | Value |
|---|---:|
| LLM input tokens | 0 |
| LLM output tokens | 0 |
| Agent wall-clock | 0 |
| Training wall-clock | 0 |
| GPU-hours | 0 |
| Iterations | 0 |
| Failures / retries | 0 / 0 |

## 20. Repository status

| Component | Status |
|---|---|
| Repository structure | `IMPLEMENTED` |
| Coordination docs | `IMPLEMENTED` |
| Architecture docs | `IMPLEMENTED` |
| Starter kit preservation | `IMPLEMENTED` |
| Evaluation adapter | `IMPLEMENTED` (thin wrapper, tested) |
| Data adapter | `IMPLEMENTED` (split-guarded) |
| Experiment registry | `IMPLEMENTED` (schema + read/write, tested) |
| Convergence tracker | `IMPLEMENTED` (tested) |
| Feature framework | `SCAFFOLDED` (ABC only) |
| Model framework | `SCAFFOLDED` (ABC only) |
| Training loop | `PLANNED` |
| Agent loop | `SCAFFOLDED` (control-flow skeleton, no LLM calls) |
| Runtime / recovery | `PLANNED` |
| Resource accounting | `SCAFFOLDED` (schema only) |
| Official baseline reproduction | `PLANNED` |

## 21. Current next actions

1. **Everyone** — complete `docs/runbooks/LOCAL_SETUP.md`, confirm
   `--model random` gives Primary ≈ 0.475.
2. **Min** — open the GitHub repo, add all five as collaborators, protect `main`,
   create the five workstream branches.
3. **Sarthak** — execute `docs/runbooks/BASELINE_REPRODUCTION.md`, record
   `EXP-0000-OFFICIAL-BASELINE` in `experiments/baseline/`.
4. **Rishi** — EDA on train/valid only; produce a feature inventory. Read the rejected
   list in §16 first.
5. **Vidush** — draft the pairwise/listwise loss experiment plan (`H-001`).
6. **Nandit** — implement the run logger and resource monitor against the schemas in
   `src/logging/` and `src/monitoring/`.
