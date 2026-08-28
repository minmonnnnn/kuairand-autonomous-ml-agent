# Runbook · Running an Experiment

Owner: Min · Consumers: everyone

## Before you run

1. Is there a hypothesis? Non-trivial experiments need one
   (`docs/research/hypotheses/HYPOTHESIS_TEMPLATE.md`).
2. Is `EXP-0000-OFFICIAL-BASELINE` `VALIDATED`? If not, stop.
3. What is the parent experiment? Every experiment compares against a specific parent,
   not vaguely against "the baseline".
4. Have you changed exactly one thing? Two changes give you one uninterpretable number.
5. Is this already on the rejected list (`TEAM_SOT.md` §16)? If so, you need a documented
   reason in `research/rejected/`.

## Allocate an ID

IDs are immutable, sequential, and never reused:

```bash
python3 -c "from src.registry.registry import next_experiment_id; print(next_experiment_id())"
```

## Run

Single seed, for a quick directional read:

```bash
python3 scripts/experiments/run_experiment.py --config configs/experiments/EXP-0007.yaml --seed 0
```

Multi-seed, required before accepting any result:

```bash
python3 scripts/experiments/run_experiment.py --config configs/experiments/EXP-0007.yaml --seeds 0 1 2
```

## Interpreting the number

Seed std on Primary is **0.0008**. So:

| Observed valid Primary delta | Verdict |
|---|---|
| < 0.0016 (2σ), single seed | `NEUTRAL` — this is noise. Not a result. |
| ≥ 0.0016, single seed | Promising. Re-run over ≥3 seeds before believing it. |
| ≥ 0.0016, mean over ≥3 seeds, non-overlapping std | `IMPROVEMENT` |
| ≤ −0.0016, mean over ≥3 seeds | `REGRESSION` — record it, do not delete it |

The convergence rule (ε = 0.002, N = 3) is deliberately set just above 2σ. That is not a
coincidence — it exists so that noise cannot masquerade as progress.

## Record it

Every experiment gets a record in `experiments/<area>/EXP-NNNN.json`, whether it
succeeded, failed, crashed, or was abandoned. Failed experiments are research evidence
and are graded as such.

Required fields: see `src/registry/schema.py`. At minimum you must have
`experiment_id`, `parent_experiment`, `hypothesis_id`, `owner`, `changes`, `config`,
`feature_version`, `seed(s)`, validation metrics, deltas, wall-clock, `git_commit`,
`status`, and `notes`.

## Reflect

After recording, write two or three sentences in the record's `notes`:

- Did it do what the hypothesis predicted?
- If not, is that because the mechanism is wrong, or the implementation is wrong?
- What does this rule in or out for the next experiment?

That last question is the point of the whole exercise. An experiment that does not
change what you try next was a wasted iteration out of fifty.
