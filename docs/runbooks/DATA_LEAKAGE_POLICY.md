# Runbook · Data Leakage Policy

Owner: Min · Enforced in code by `src/data/guard.py` · Status: `IMPLEMENTED`

## Split classification

| Split | Dates | Class | Usable for |
|---|---|---|---|
| train | 20220408–20220421 | `DEVELOPMENT` | fitting anything |
| valid | 20220422–20220428 | `VALIDATION` | model selection, tuning, convergence |
| test | 20220429–20220508 | `FINAL-ONLY` | scoring the final submission, once |

## The uncomfortable fact

The test labels are physically present in the downloaded dataset. Nothing stops anyone
from reading them. The "hidden" test is therefore **self-policed**, and the integrity of
every result we report depends on us actually policing it. This is recorded as `KI-001`
in `TEAM_SOT.md` so nobody mistakes the code guard for a real barrier.

## Prohibited uses of the test split

The test split must never influence:

- feature selection
- hyperparameter tuning
- model selection
- hypothesis selection
- convergence decisions
- agent feedback or reflection
- experimentation of any kind
- debugging based on labels

That last one is the sneaky one. "Let me just check whether it also drops on test"
is leakage even if you change nothing afterwards, because you cannot un-know it.

## What is allowed

- Reading the **structure** of the test split: row count, user count, duplicate-pair
  rate, split date range. These are published in the starter kit already.
- Producing test **scores** for the final submission, from the already-designated
  validation-best checkpoint.
- Quoting the organizers' published test numbers for the baselines and oracle ceiling.

## Enforcement in code

```python
from src.data.loader import load_splits
from src.data.guard import Split, FinalSubmissionToken

splits = load_splits(data_dir)              # train + valid only
splits = load_splits(data_dir, Split.TEST)  # raises SplitAccessError

# The only legitimate path, used once, in the submission workflow:
token = FinalSubmissionToken.issue(
    experiment_id="EXP-0031",
    reason="final submission from designated validation-best checkpoint",
)
splits = load_splits(data_dir, Split.TEST, token=token)
```

Issuing a token writes an audit line to `logs/errors/split_access.log` recording who,
when, which experiment, and why. If that log has entries that are not the final
submission, we have a problem worth discussing openly.

## Model selection rule

Early stopping, checkpoint selection, convergence checks and the validation-best
designation all use **validation Primary**. Never test. This is checked at review time —
any PR where a test metric appears in a selection path is rejected.

## Unbiased validation (advanced, allowed)

`log_random_4_22_to_5_08_pure.csv` is a random-exposure log of ~1.18M rows over the
valid+test window. It is a legitimate **additional validation** signal for checking
whether a model only works on biased traffic. Treat any part of it falling in the test
date range with the same care as the test split — use it for diagnosis of a chosen
model, not for selection.

## If leakage happens

Say so. Immediately, in the SOT under Known Issues, and in the affected experiment
records. Then invalidate every downstream decision that could have been influenced.

A disclosed leak costs some experiments. An undisclosed one invalidates the whole
project's claims, and the challenge is explicitly grading auditability.
