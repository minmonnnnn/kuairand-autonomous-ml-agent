# ORGANIZER REFERENCE CODE — DO NOT MODIFY

Every file in this directory except this one is supplied by the challenge organizers and
is preserved **verbatim**. CI fails any pull request that changes them.

| File | Role |
|---|---|
| `evaluate.py` | The metric definition. GAUC, nDCG@5, primary. **The only definition in this project.** |
| `data.py` | Data loading, official splits, feature encoding. Defines the row order that `row_id` depends on. |
| `baseline.py` | Three baselines: `fm` (the one to beat), `pop`, `random` (harness self-check). |
| `submit.py` | Submission generation and validation. |
| `ablation_features.py` | Reproduces the organizers' "extra static features give no gain" result. |
| `baseline_scores.json` | Published scores, seed variance, convergence parameters. |
| `README.md` | Organizer documentation (Chinese). English digest: `docs/research/STARTER_KIT_NOTES.md`. |

## If you need different behaviour

Write an adapter in `src/`. That is what `src/data/loader.py` and
`src/evaluation/official.py` already do — they import these modules rather than
copying or replacing them.

## Why this rule is strict

If the evaluator drifts, every number in the repository becomes incomparable, including
against the organizers' published baseline. If the loader's row order drifts, the
submission misaligns and `submit.py --check` fails at the very end, after the work is
done. Both failures are silent until they are expensive.
