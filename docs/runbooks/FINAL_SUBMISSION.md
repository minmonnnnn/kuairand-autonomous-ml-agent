# Runbook · Final Submission

Owner: Min · Task: `T-105` · Milestone: `M5`

**This is the only point at which the test split may be read.** Everything before this
uses train and valid only.

## Preconditions

- [ ] The run has terminated with a recorded state: `CONVERGED`, `MAX_ITERATIONS`, or `TIMEOUT`
- [ ] The validation-best checkpoint is designated in the registry, with its experiment ID
- [ ] That experiment's record is complete: config hash, feature version, seed, git commit
- [ ] `EXP-0000-OFFICIAL-BASELINE` is `VALIDATED` so the delta is meaningful
- [ ] The checkpoint loads cleanly and reproduces its recorded validation metrics

Do not assume the latest experiment is the best experiment. Read the registry.

## Procedure

### 1. Reconfirm the validation-best

```bash
python3 -c "
from src.registry.registry import ExperimentRegistry
r = ExperimentRegistry()
print(r.validation_best())
"
```

Re-score the validation split from the checkpoint and confirm it matches the recorded
number. If it does not, the checkpoint or the pipeline has drifted — stop and diagnose.

### 2. Score the test split

```bash
python3 scripts/submission/make_submission.py \
    --experiment EXP-NNNN \
    --split test \
    --out artifacts/submissions/final_submission.csv
```

This is the one code path that issues a `FinalSubmissionToken` and writes an audit line
to `logs/errors/split_access.log`.

### 3. Validate the file

```bash
cd starter_kit
python3 submit.py --check --split test --data_dir ../KuaiRand-Pure/data \
    ../artifacts/submissions/final_submission.csv
```

The checker rejects: wrong header, wrong row count, skipped `row_id`,
`user_id`/`video_id` misalignment, non-numeric scores, NaN, Inf.

### 4. Manual checklist

- [ ] Header is exactly `row_id,user_id,video_id,score`
- [ ] Exactly **170,588** data rows
- [ ] `row_id` starts at 0 and increases by 1 with no gaps
- [ ] Scores are finite reals — only relative order matters, any scale is fine
- [ ] Row order matches contract C-01 (nothing was sorted or grouped anywhere)
- [ ] No deduplication was applied — 3.06% of `(user_id, video_id)` pairs repeat, up to
      12 times, and every occurrence needs its own row

### 5. Archive

Store alongside the submission: the experiment ID, config hash, feature version, seed,
git commit, checkpoint path, and the validation metrics it was selected on.

### 6. Final report

`artifacts/reports/FINAL_RESULTS.md` must contain:

- GAUC, nDCG@5, Primary (validation; test only once the organizers report it)
- delta vs the official baseline
- total iterations and terminal state
- LLM input / output / total tokens
- agent wall-clock, training wall-clock, GPU-hours if any
- manual interventions and what triggered each
- failures, retries, automatic recoveries
- what worked, what did not, and what we would do next

Report the honest number. A modest improvement with a clean audit trail is worth more
here than an unverifiable large one — technical execution, autonomy and feasibility
together outweigh raw accuracy in the rubric.
