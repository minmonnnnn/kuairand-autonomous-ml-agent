# Task Board

Statuses: `NOT STARTED` · `IN PROGRESS` · `BLOCKED` · `READY FOR INTEGRATION` ·
`INTEGRATED` · `VALIDATED`

Milestones: `M0` foundation · `M1` official baseline · `M2` independent workstreams ·
`M3` first autonomous iteration · `M4` robust autonomous run · `M5` competition run

> Update the status line of your own tasks in the same PR as the work. Add new tasks
> freely inside your workstream; cross-workstream tasks need a change request.

---

## T-000 · Everyone · Local setup

| | |
|---|---|
| Owner | All five |
| Workstream | — |
| Priority | P0 |
| Status | NOT STARTED |
| Dependencies | none |
| Files owned | none |
| Files forbidden | `starter_kit/**` |
| Deliverable | Working local environment with the dataset |
| Acceptance criteria | `python3 baseline.py --model random` prints Primary ≈ 0.475 (±0.001) on test |
| Target milestone | M0 |

Follow `docs/runbooks/LOCAL_SETUP.md`. If the random sanity check fails, stop and fix
the harness before anything else — the organizers say so explicitly.

---

# MIN — Architecture, orchestration, integration

## T-101 · GitHub repository and branch protection

| | |
|---|---|
| Priority | P0 · **Status** NOT STARTED · **Milestone** M0 |
| Dependencies | none |
| Files owned | `.github/**` |
| Deliverable | Repo created, 5 collaborators added, `main` protected, 5 workstream branches pushed |
| Acceptance criteria | Every teammate can push to their own branch and open a PR; direct pushes to `main` are rejected; CODEOWNERS auto-requests reviews |

## T-102 · Experiment registry

| | |
|---|---|
| Priority | P0 · **Status** IN PROGRESS (schema + I/O scaffolded) · **Milestone** M0 |
| Dependencies | none |
| Files owned | `src/registry/**` |
| Files forbidden | `src/evaluation/**`, `src/models/**` |
| Deliverable | `ExperimentRecord` schema, append-only JSON store, validation-best tracking, ID allocation |
| Acceptance criteria | Round-trips a record; refuses duplicate IDs; recomputes `is_validation_best` correctly across a synthetic set of 10 experiments; `tests/unit/test_registry.py` passes |

## T-103 · Config system

| | |
|---|---|
| Priority | P1 · **Status** NOT STARTED · **Milestone** M2 |
| Dependencies | T-102 |
| Files owned | `configs/**`, `src/orchestration/config.py` |
| Deliverable | Layered YAML config (base → model → features → experiment) with a resolved-config hash recorded per experiment |
| Acceptance criteria | Same resolved config produces the same hash; the hash is stored on every experiment record |

## T-104 · Agent loop skeleton

| | |
|---|---|
| Priority | P1 · **Status** NOT STARTED · **Milestone** M3 |
| Dependencies | T-102, T-103, T-301, T-401 |
| Files owned | `src/agent/**`, `src/orchestration/**` |
| Files forbidden | `src/features/**`, `src/models/**`, `src/runtime/**` |
| Deliverable | hypothesis → plan → execute → evaluate → record → reflect → select, running end to end with stub components |
| Acceptance criteria | Three consecutive iterations complete without human input, each producing a registry record and an iteration log |

## T-105 · Final submission workflow

| | |
|---|---|
| Priority | P2 · **Status** NOT STARTED · **Milestone** M5 |
| Dependencies | T-102, T-303 |
| Files owned | `scripts/submission/**`, `src/orchestration/submission.py` |
| Deliverable | Validation-best checkpoint → scores → CSV → `submit.py --check` → archived artifact |
| Acceptance criteria | Produces a file that passes `--check` on the test split with the correct 170,588 rows and strictly increasing `row_id` |

---

# RISHI — Data & features

## T-201 · Data loader adapter with split guard

| | |
|---|---|
| Priority | P0 · **Status** IN PROGRESS (scaffolded) · **Milestone** M1 |
| Dependencies | T-000 |
| Files owned | `src/data/**`, `tests/data/**` |
| Files forbidden | `starter_kit/**`, `src/models/**` |
| Deliverable | Adapter over `starter_kit/data.py` that enforces the DEVELOPMENT / VALIDATION / FINAL-ONLY split policy |
| Acceptance criteria | Row counts match 1,141,112 / 124,909 / 170,588 exactly; requesting `test` without an explicit final-submission token raises `SplitAccessError`; row order matches contract C-01 |

## T-202 · EDA and feature inventory

| | |
|---|---|
| Priority | P0 · **Status** NOT STARTED · **Milestone** M2 |
| Dependencies | T-201 |
| Files owned | `notebooks/exploration/`, `docs/research/features/` |
| Deliverable | `docs/research/features/FEATURE_INVENTORY.md` — every available column, its type, cardinality, missingness, and a judgement on whether it can affect within-user ranking |
| Acceptance criteria | Covers all files in KuaiRand-Pure; explicitly marks which candidates are already-rejected static features; uses train + valid only |

**Constraint that shapes this task:** pure user-side first-order features contribute
exactly zero to within-user ranking. Mark every user-side column with how it would have
to be crossed with an item-side signal to matter.

## T-203 · Feature framework

| | |
|---|---|
| Priority | P1 · **Status** SCAFFOLDED (ABC only) · **Milestone** M2 |
| Dependencies | T-201 |
| Files owned | `src/features/**`, `tests/features/**`, `configs/features/` |
| Deliverable | `FeatureBuilder` ABC + registry + versioning, emitting `FeatureBundle` per contract C-02 |
| Acceptance criteria | A builder reproducing the official 5 fields produces a bundle that trains to the baseline number; vocabularies demonstrably fit on train only |

## T-204 · Behavioural and temporal features

| | |
|---|---|
| Priority | P1 · **Status** NOT STARTED · **Milestone** M2 |
| Dependencies | T-202, T-203 |
| Files owned | `src/features/**`, `experiments/features/` |
| Deliverable | Candidate families: within-user impression rank, user×item-popularity crosses, recency, session/time-of-day (`hourmin`), historical feedback aggregates |
| Acceptance criteria | Each family is a separate feature version with its own ablation; each is compared over ≥3 seeds against its parent experiment |

---

# VIDUSH — Models & training

## T-301 · Model interface + FM reimplementation parity

| | |
|---|---|
| Priority | P0 · **Status** SCAFFOLDED (ABC only) · **Milestone** M1 |
| Dependencies | T-203 |
| Files owned | `src/models/**`, `tests/models/**` |
| Files forbidden | `starter_kit/**`, `src/features/**` |
| Deliverable | `RankingModel` ABC + an FM in our framework matching the organizer FM |
| Acceptance criteria | Our FM reaches valid Primary within 0.002 of 0.6016 on seed 0, and within 0.0016 mean over seeds 0–4 |

This is the parity gate. Nothing downstream is trustworthy until our FM matches theirs.

## T-302 · Pairwise / listwise loss (H-001)

| | |
|---|---|
| Priority | P0 · **Status** NOT STARTED · **Milestone** M2 |
| Dependencies | T-301 |
| Files owned | `src/training/**`, `src/models/**`, `experiments/models/` |
| Deliverable | BPR pairwise loss and within-user softmax listwise loss on the same FM backbone |
| Acceptance criteria | Both run to convergence over ≥3 seeds; results recorded whether positive or negative; compared against `EXP-0000` |

The organizers name this the most likely source of gain: the objective is pointwise
while the metrics are ranking metrics.

## T-303 · Training loop and checkpointing

| | |
|---|---|
| Priority | P1 · **Status** NOT STARTED · **Milestone** M2 |
| Dependencies | T-301 |
| Files owned | `src/training/**`, `artifacts/checkpoints/` |
| Deliverable | Trainer producing `TrainingResult` per contract C-03, with best-validation checkpointing and early stopping |
| Acceptance criteria | Selects on validation Primary only; `(config, seed, feature_version)` reproduces identically; raises `TrainingDiverged` on NaN rather than saving |

## T-304 · Multi-task auxiliary feedback

| | |
|---|---|
| Priority | P2 · **Status** NOT STARTED · **Milestone** M3 |
| Dependencies | T-302 |
| Files owned | `src/models/**`, `src/training/**` |
| Deliverable | Multi-task head over `is_click`, `is_like`, `is_follow`, `is_comment`, `is_forward`, `play_time_ms` with `long_view` as the main task |
| Acceptance criteria | Task weighting is configurable; measured, not assumed to help; negative results recorded |

---

# SARTHAK — Evaluation, experimental science, research

## T-401 · Evaluation adapter

| | |
|---|---|
| Priority | P0 · **Status** IMPLEMENTED (thin wrapper) · **Milestone** M1 |
| Dependencies | T-000 |
| Files owned | `src/evaluation/**`, `tests/evaluation/**` |
| Files forbidden | `starter_kit/**` |
| Deliverable | Adapter importing `starter_kit/evaluate.py`, plus score validation and diagnostics |
| Acceptance criteria | Numerically identical to calling `evaluate()` directly on random inputs; rejects NaN/Inf; random-score anchor reproduces Primary ≈ 0.475 on test |

## T-402 · Reproduce the official baseline → `EXP-0000`

| | |
|---|---|
| Priority | P0 · **Status** NOT STARTED · **Milestone** M1 |
| Dependencies | T-401, T-201 |
| Files owned | `experiments/baseline/`, `docs/runbooks/BASELINE_REPRODUCTION.md` (with Min) |
| Deliverable | `EXP-0000-OFFICIAL-BASELINE` recorded, seeds 0–4, valid + our own reproduced numbers |
| Acceptance criteria | Valid Primary within 0.002 of 0.6016; submission generation and `--check` both verified; record committed |

**No improvement claim may be made before this is `VALIDATED`.**

## T-403 · Variance and significance framework

| | |
|---|---|
| Priority | P0 · **Status** NOT STARTED · **Milestone** M2 |
| Dependencies | T-402 |
| Files owned | `src/experiments/**`, `experiments/analysis/` |
| Deliverable | Multi-seed runner, seed-variance reporting, `EvaluationSummary` classification per contract C-05 |
| Acceptance criteria | Reproduces the published 0.0008 seed std; classifies a sub-2σ single-seed delta as `NEUTRAL`, never `IMPROVEMENT` |

## T-404 · Convergence tracker

| | |
|---|---|
| Priority | P1 · **Status** IMPLEMENTED (tested) · **Milestone** M3 |
| Dependencies | T-402 |
| Files owned | `src/experiments/convergence.py` |
| Deliverable | Tracks all three termination conditions: `CONVERGED` (ε=0.002, N=3), `MAX_ITERATIONS` (50), `TIMEOUT` (6h) |
| Acceptance criteria | Unit-tested against hand-built metric sequences including boundary cases at exactly 0.002 |

## T-405 · Literature and public-solution review

| | |
|---|---|
| Priority | P1 · **Status** NOT STARTED · **Milestone** M2 |
| Dependencies | none |
| Files owned | `research/papers/`, `research/public_solutions/`, `docs/research/literature/` |
| Deliverable | Reviewed notes on BPR / listwise ranking losses, DIN / SIM sequence models, CWM censored watch-time regression, multi-task recommenders |
| Acceptance criteria | Each review ends in a concrete hypothesis added to `research/hypothesis_queue/`, or an explicit rejection with reasoning |

---

# NANDIT — Runtime, robustness, resources

## T-501 · Run logger

| | |
|---|---|
| Priority | P0 · **Status** SCAFFOLDED (schema only) · **Milestone** M2 |
| Dependencies | none |
| Files owned | `src/logging/**`, `logs/` |
| Deliverable | Structured per-iteration JSON log matching the schema in `src/logging/schema.py` |
| Acceptance criteria | Every iteration writes exactly one record including errors and recovery actions; logs survive a crashed run |

## T-502 · Resource monitor

| | |
|---|---|
| Priority | P0 · **Status** SCAFFOLDED (schema only) · **Milestone** M2 |
| Dependencies | T-501 |
| Files owned | `src/monitoring/**`, `logs/resources/` |
| Deliverable | Wall-clock, CPU time, peak memory, GPU-hours, iteration count, failures, retries, manual interventions |
| Acceptance criteria | Totals reconcile against an independent `/usr/bin/time` measurement within 5% |

## T-503 · LLM token accounting

| | |
|---|---|
| Priority | P0 · **Status** NOT STARTED · **Milestone** M3 |
| Dependencies | T-502 |
| Files owned | `src/llm/**` |
| Deliverable | Input/output/total token accounting per agent call, aggregated per iteration and per run |
| Acceptance criteria | Per-call totals reconcile against provider-reported usage; a run report can be produced at any point mid-run |

## T-504 · Experiment runner with timeout and retry

| | |
|---|---|
| Priority | P1 · **Status** NOT STARTED · **Milestone** M4 |
| Dependencies | T-501 |
| Files owned | `src/runtime/**`, `tests/runtime/**` |
| Files forbidden | `src/models/**`, `src/features/**` |
| Deliverable | Subprocess execution producing `RunResult` per contract C-06, with timeouts, retries, and output validation |
| Acceptance criteria | Every run yields a `RunResult` including crashes and timeouts; no silent failures |

## T-505 · Recovery manager

| | |
|---|---|
| Priority | P1 · **Status** NOT STARTED · **Milestone** M4 |
| Dependencies | T-504 |
| Files owned | `src/reliability/**`, `tests/reliability/**` |
| Deliverable | Failure classification → `RETRY` / `RETRY_WITH_PATCH` / `ROLLBACK` / `SKIP` / `ESCALATE` |
| Acceptance criteria | Injected failure suite (invalid config, missing data, malformed data, crash, timeout, NaN, Inf, bad checkpoint, invalid submission, subprocess kill) is recovered without human input except where `ESCALATE` is genuinely correct; each escalation increments `manual_interventions` |
