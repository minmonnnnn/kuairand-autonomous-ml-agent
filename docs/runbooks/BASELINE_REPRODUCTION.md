# Runbook · Official Baseline Reproduction

Owner: Sarthak (execution) · Min (record) · Task: `T-402` · Milestone: `M1`

**No improvement claim may be made by anyone until this runbook completes and
`EXP-0000-OFFICIAL-BASELINE` is recorded as `VALIDATED`.**

## Why this comes first

The official baseline is the organizers' number, produced by their code. A number we
produce ourselves is only meaningful if we can first reproduce theirs. If we cannot,
the discrepancy is in our harness, and everything built on top of it is unreliable.

Distinguish carefully, in every document and every commit:

```text
OFFICIAL ORGANIZER BASELINE     their code, their number
TEAM BASELINE                   our reimplementation, verified against theirs
EXPERIMENTAL MODELS             everything after that
```

## Procedure

### Step 1 — Confirm the splits

```bash
cd starter_kit
python3 -c "
from data import load
s = load('../KuaiRand-Pure/data')
print({k: len(v) for k, v in s.items()})
"
```

Must print exactly `{'train': 1141112, 'valid': 124909, 'test': 170588}`.

### Step 2 — Confirm the evaluator

```bash
python3 baseline.py --model random --data_dir ../KuaiRand-Pure/data
```

Test Primary must be ≈ 0.4753 (±0.001). This is the organizers' prescribed self-check.

### Step 3 — Confirm the trivial rung

```bash
python3 baseline.py --model pop --data_dir ../KuaiRand-Pure/data
```

Expected: valid Primary ≈ 0.5807, test ≈ 0.5715.

### Step 4 — Run the official FM, all five seeds

```bash
for s in 0 1 2 3 4; do
  python3 baseline.py --model fm --seed $s --data_dir ../KuaiRand-Pure/data \
    | tee ../logs/iterations/exp0000_seed$s.log
done
```

Reference (`baseline_scores.json`):

| Split | GAUC | nDCG@5 | Primary |
|---|---:|---:|---:|
| valid | 0.6674 | 0.5357 | 0.6016 |
| test | 0.6610 | 0.5282 | 0.5946 |

Config: FM, `k=16`, `lr=0.001`, batch 8192, max 40 epochs, patience 4, fields
`[user_id, video_id, author_id, tab, dur_bucket]`.

**Acceptance:** mean valid Primary within **0.002** of 0.6016, and observed seed std of
the same order as the published 0.0008.

### Step 5 — Verify submission generation

```bash
python3 submit.py --make --split valid --data_dir ../KuaiRand-Pure/data ../artifacts/submissions/exp0000_valid.csv
python3 submit.py --check --split valid --data_dir ../KuaiRand-Pure/data ../artifacts/submissions/exp0000_valid.csv
python3 submit.py --score --split valid --data_dir ../KuaiRand-Pure/data ../artifacts/submissions/exp0000_valid.csv
```

`--check` must pass and `--score` must agree with Step 4's valid numbers.

> Use `--split valid` here. Generating a test submission is part of the *final*
> workflow, not baseline verification.

### Step 6 — Record the experiment

Create `experiments/baseline/EXP-0000.json` per `src/registry/schema.py`:

- `experiment_id: EXP-0000-OFFICIAL-BASELINE`
- `parent_experiment: null`
- `owner: Sarthak`
- `status: VALIDATED`
- all five seeds' validation metrics, plus mean and std
- `git_commit`, config hash, wall-clock per seed
- `notes`: any deviation from the published numbers, however small

### Step 7 — Update the SOT

Set `TEAM_SOT.md` §6 (validation-best), §20 (baseline reproduction → `VALIDATED`),
and §21 (next actions).

## If reproduction fails

Do not proceed and do not adjust the target to match what you got. Debug in this order:

1. Wrong dataset variant (Pure vs 1K vs 27K)
2. Modified `starter_kit/` files — `git diff starter_kit/` must be empty
3. numpy version differences in RNG behaviour
4. Row-order violation in a custom loader — verify against contract C-01

Record the investigation in `experiments/baseline/` even if it turns out to be a
trivial mistake. That is exactly the audit trail the challenge is asking for.
