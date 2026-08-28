# Data Flow

Status: `SCAFFOLDED` · Owner: Min

## End-to-end path

```text
KuaiRand-Pure/data/*.csv                       [on disk, git-ignored]
        │
        │  starter_kit/data.py :: load()       [ORGANIZER REFERENCE — unmodified]
        ▼
src/data/loader.py                             [Rishi — adapter + split guard]
        │  RawSplits: train / valid / test     [contract C-01]
        │  test is gated behind SplitAccessError
        ▼
src/features/*.py                              [Rishi — FeatureBuilder]
        │  FeatureBundle(X, y, users, dense,   [contract C-02]
        │                field_dims, version)
        │  vocabularies fit on TRAIN ONLY
        ▼
src/models/*.py + src/training/*.py            [Vidush]
        │  TrainingResult(checkpoint, metrics) [contract C-03]
        │  model selection on VALID ONLY
        ▼
scores: np.ndarray                             [aligned to row order from C-01]
        │
        ▼
src/evaluation/official.py                     [Sarthak — thin adapter]
        │  → starter_kit/evaluate.py           [ORGANIZER REFERENCE — authoritative]
        │  {GAUC, nDCG@5, primary}             [contract C-04]
        ▼
src/experiments/*.py                           [Sarthak]
        │  EvaluationSummary + significance    [contract C-05]
        ▼
src/registry/                                  [Min]
        │  ExperimentRecord → experiments/*.json
        │  is_validation_best recomputed
        ▼
agent critic + experiment selector             [Min]
        │
        └──▶ next ExperimentSpec  (loop)

... at termination ...

validation-best checkpoint
        ▼
score the TEST split                           [first and only legitimate test access]
        ▼
scripts/submission/                            [Min]
        │  row_id,user_id,video_id,score
        ▼
starter_kit/submit.py --check                  [ORGANIZER REFERENCE — must pass]
        ▼
artifacts/submissions/
```

## Row-order invariant

The submission `row_id` is defined by the order `starter_kit/data.py` produces rows:
`log_standard_4_08_to_4_21_pure.csv` first, then
`log_standard_4_22_to_5_08_pure.csv`, date-filtered, original file order preserved.

**Nothing in the pipeline may reorder rows.** Features, models and evaluation all
operate on that fixed order. Shuffling happens only over *indices* inside the training
loop, never over the stored arrays.

`(user_id, video_id)` is **not** a key — the test split has 3.06% duplicate pairs, up to
12 repeats. Never join on it; always carry the row index.

## Split access policy

| Split | Class | Who may read it | When |
|---|---|---|---|
| train | DEVELOPMENT | everyone | always |
| valid | VALIDATION | everyone | always |
| test | **FINAL-ONLY** | submission workflow only | once, after the validation-best checkpoint is designated |

Enforced in code by `src/data/guard.py`; enforced in practice by
`docs/runbooks/DATA_LEAKAGE_POLICY.md`.
