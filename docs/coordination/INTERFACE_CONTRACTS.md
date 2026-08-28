# Interface Contracts

Version: `v0` · Status: `SCAFFOLDED` · Owner: Min

These are the seams between workstreams. They exist so that Rishi can change every line
of his feature code without breaking Vidush, and vice versa.

**Rules:**

- Every contract has an owner, a consumer, a schema, invariants, a version, and a
  defined failure behaviour.
- Changing a contract requires a change request (`CHANGE_REQUEST_PROCESS.md`).
- Adding an optional field is backward-compatible. Removing or renaming a field is not.
- Bump the version on any breaking change and update every consumer in the same PR.

---

## C-01 · Data → Features

**Owner:** Rishi · **Consumer:** Rishi (features), Sarthak (analysis)

**Input:** a split name and a data directory.

**Output:**

```python
RawSplits = dict[str, list[Row]]      # 'train' | 'valid' | 'test'
Row = tuple[int, str, str, str, str, float, int]
#       date, user_id, video_id, author_id, tab, duration_ms, label
```

**Invariants**

- Row order is deterministic: `log_standard_4_08_to_4_21_pure.csv` is read before
  `log_standard_4_22_to_5_08_pure.csv`; within each file, original file order is
  preserved after date filtering. **Submission `row_id` depends on this.**
- `label` is `long_view`, cast to `{0, 1}`.
- Row counts: train 1,141,112 · valid 124,909 · test 170,588.

**Failure behaviour:** raise on missing files or unexpected row counts. Never
silently return a partial split.

**Guard:** requesting `test` outside a designated final-submission context raises
`SplitAccessError`. See `src/data/guard.py`.

---

## C-02 · Features → Models

**Owner:** Rishi · **Consumer:** Vidush

**Output of a `FeatureBuilder`:**

```python
@dataclass
class FeatureBundle:
    X: np.ndarray            # int32, shape (N, F) — offset-encoded categorical ids
    y: np.ndarray            # float32, shape (N,) — the long_view label
    users: list[str]         # length N — user_id per row, for grouped evaluation
    dense: np.ndarray | None # float32, (N, D) or None — dense features, if any
    field_dims: list[int]    # per-field vocabulary size (incl. one UNK slot each)
    total_dim: int           # sum(field_dims) — embedding table size
    feature_version: str     # e.g. "fv-003"
    metadata: dict           # field names, encoder config, build timestamp
```

**Invariants**

- `len(X) == len(y) == len(users)` and, if present, `len(dense)`.
- Vocabularies are fit on **train only**. Unseen values in valid/test map to that
  field's UNK slot. No exceptions — fitting on valid is leakage.
- `X` values are already offset into the shared embedding table
  (`offsets = cumsum([0] + field_dims[:-1])`).
- Row order matches C-01 exactly. Models must not reorder rows.
- `feature_version` is immutable once used in a recorded experiment.

**Failure behaviour:** raise `FeatureBuildError` with the field that failed. Never
emit NaN or negative ids.

---

## C-03 · Models → Training

**Owner:** Vidush · **Consumer:** Vidush, Nandit (execution)

**Input:** a model instance, a training config, a `FeatureBundle` per split.

**Output:**

```python
@dataclass
class TrainingResult:
    checkpoint_path: str
    best_epoch: int
    epochs_run: int
    train_metrics: list[dict]     # per-epoch loss etc.
    valid_metrics: list[dict]     # per-epoch GAUC / nDCG@5 / primary
    wall_clock_seconds: float
    early_stopped: bool
    seed: int
```

**Invariants**

- Model selection uses **validation Primary only**. Never test.
- The returned checkpoint is the **best-validation** state, not the last state.
- A given `(config, seed, feature_version)` reproduces bit-identically on the same
  machine.

**Failure behaviour:** on NaN/Inf loss, stop, save nothing, raise `TrainingDiverged`
with the epoch and batch index. Nandit's runtime catches this and decides retry vs
rollback.

---

## C-04 · Training → Evaluation

**Owner:** Sarthak · **Consumer:** everyone

**Input:** three equal-length sequences — `user_ids`, `labels`, `scores`.

**Output:**

```python
{'GAUC': float, 'nDCG@5': float, 'primary': float, 'users': int, 'rows': int}
```

**Invariants**

- The implementation is `starter_kit/evaluate.py`, imported, never copied, never
  reimplemented. `src/evaluation/official.py` is a thin adapter over it.
- `primary == (GAUC + nDCG@5) / 2`.
- `scores` are arbitrary reals; only relative order matters. NaN/Inf are rejected
  before evaluation.
- Sanity anchor: random scores must produce Primary ≈ 0.475 (±0.001) on test,
  ≈ 0.483 on valid. If not, the harness is broken — fix it before anything else.

**Failure behaviour:** raise on length mismatch or non-finite scores.

---

## C-05 · Evaluation → Agent

**Owner:** Sarthak · **Consumer:** Min (agent)

**Output:**

```python
@dataclass
class EvaluationSummary:
    experiment_id: str
    metrics: dict                    # C-04 output
    delta_vs_official_baseline: float
    delta_vs_parent: float
    classification: str              # IMPROVEMENT | REGRESSION | NEUTRAL | INVALID
    significant: bool                # |delta| > 2 sigma (0.0016 primary)
    seeds_run: int
    seed_std: float | None
    diagnostics: dict                # per-segment breakdown, user buckets
    recommendation: str              # what the agent should consider next
```

**Invariants**

- `NEUTRAL` is returned whenever `|delta| <= 0.0016` and `seeds_run == 1`. A single-seed
  movement below 2σ is never `IMPROVEMENT`.
- `INVALID` for failed runs, non-finite scores, or misaligned row counts.
- `recommendation` is advisory. The agent's Experiment Selector decides.

---

## C-06 · Agent → Runner

**Owner:** Min (spec) / Nandit (runner) · **Consumer:** Nandit

**Input:**

```python
@dataclass
class ExperimentSpec:
    experiment_id: str
    parent_experiment: str | None
    hypothesis_id: str
    config_path: str
    feature_version: str
    model_name: str
    seed: int
    timeout_seconds: int
    max_retries: int
```

**Output:**

```python
@dataclass
class RunResult:
    experiment_id: str
    status: str                  # SUCCESS | FAILED | TIMEOUT | INVALID_OUTPUT
    artifacts: dict              # checkpoint, scores, metrics paths
    resources: dict              # wall clock, peak memory, cpu, gpu hours
    errors: list[dict]
    recovery_actions: list[dict]
    retries: int
    stdout_path: str
    stderr_path: str
```

**Invariants**

- The runner never interprets metrics. It reports execution facts only.
- Every run produces a `RunResult`, including crashed ones. Silent failure is a bug.

---

## C-07 · Runner → Recovery Manager

**Owner:** Nandit · **Consumer:** Nandit, Min

**Input:** a structured failure — error class, message, traceback, phase, retry count.

**Output:**

```python
RecoveryAction = 'RETRY' | 'RETRY_WITH_PATCH' | 'ROLLBACK' | 'SKIP' | 'ESCALATE'
```

**Invariants**

- `ESCALATE` increments `manual_interventions`. That counter is graded — every
  escalation costs autonomy score, so escalate only when no automatic route exists.
- Rollback always restores the last known-good checkpoint plus its git commit.

---

## C-08 · Experiment → Registry

**Owner:** Min · **Consumer:** everyone

Schema: `src/registry/schema.py` (`ExperimentRecord`). Records are append-only JSON
under `experiments/<area>/EXP-NNNN.json`.

**Invariants**

- `experiment_id` is immutable and never reused.
- Records are never deleted. Superseded experiments move to `experiments/archived/`
  with a `superseded_by` field.
- `is_validation_best` is set by the registry, never by hand.
- Every record carries a `git_commit`.
