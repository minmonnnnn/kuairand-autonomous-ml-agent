# Starter Kit Notes (English digest)

The organizers' `starter_kit/README.md` is written in Chinese and contains information
that materially changes what we should work on. This is a faithful digest. The original
file remains authoritative and unmodified.

Owner: Sarthak · Status: `IMPLEMENTED`

---

## 1. Task definition — fixed, not negotiable

| | |
|---|---|
| Task | Within-user ranking. Each user is ranked only over their own impressions in the evaluation set. No full-catalog retrieval. |
| Relevance label | `long_view` (native column, 0/1) |
| Metrics | GAUC, nDCG@5; **primary = mean of the two** |
| Splits | train `20220408–20220421` / valid `20220422–20220428` / test `20220429–20220508` |
| Zero-positive users | nDCG = 0, still counted in the average. GAUC counts only users with `0 < positives < impressions`, weighted by positive count. |
| nDCG gain | `2^rel − 1` (identity under binary labels) |

`evaluate.py` is the implementation and must not be changed.

## 2. The ceiling is 0.8645, not 1.0

Of the 23,875 test users:

| Group | Share | Effect |
|---|---:|---|
| All-negative (no long_view at all) | **27.1%** | nDCG permanently 0 — no model can fix this; excluded from GAUC |
| All-positive | **9.2%** | nDCG permanently 1; excluded from GAUC |
| Discriminative | **63.7%** | the actual GAUC sample |

Using true labels as scores (a perfect oracle) yields:

| | random | FM baseline | **oracle ceiling** | share of range FM captured |
|---|---:|---:|---:|---:|
| GAUC | 0.4996 | 0.6610 | 1.0000 | 32.3% |
| nDCG@5 | 0.4511 | 0.5282 | 0.7289 | 27.8% |
| **primary** | 0.4753 | **0.5946** | **0.8645** | **30.7%** |

> Measure progress against the oracle, not against 1.0. Seeing 0.5946 and concluding
> "there's a long way to 1.0" is a misreading. The baseline has already taken 30% of
> the usable range; remaining headroom is **0.27**, not 0.41.

## 3. Noise floor

FM's primary has std **0.0008** across 5 seeds. The convergence rule ε = 0.002 is
roughly 2.5σ, chosen for exactly this reason. Anything under ~0.0016 is noise.

**Self-check the organizers insist on:** if `--model random` does not give
primary ≈ 0.475 (±0.001), the harness is broken. Fix it before doing anything else.

## 4. Already tested — do not repeat

| Tried | Result |
|---|---|
| **Adding static features.** All 13 CWM feature fields (`music_id`, `video_type`, `upload_type`, plus 6 coarse user-side buckets) | primary **0.5940** vs **0.5950** for the 5-field baseline. No difference within noise; marginally worse. |
| **Adding capacity.** Embedding dimension k = 8 / 16 / 32 | 0.5895 / 0.5902 / 0.5887. Essentially flat. |

Their explanation: the `user_id × video_id` cross already absorbs most of the learnable
signal. Coarse buckets like `follow_user_num_range` are redundant given `user_id`, and
1.14M rows will not support more capacity. **The bottleneck is neither features nor
capacity.**

Reproduce with `starter_kit/ablation_features.py` if you want to see it yourself.

### The structural point that constrains all feature work

**Pure user-side first-order terms contribute exactly zero.** Ranking is within-user, so
any term that is constant across a user's rows cannot change that user's ordering. They
measured this: `item_pop × user_bias` and plain `item_pop` scored identically to the
digit. User-side features can only act **through crosses with item-side features.**

## 5. Unexplored — where the headroom should be

The organizers' own ordering, explicitly left for entrants:

1. **Change the loss.** Currently pointwise logloss while the metrics are ranking
   metrics. Pairwise (BPR) or listwise (softmax over the user's impressions) aligns the
   objective with the evaluation. **They judge this most likely to work.**
2. **User behaviour sequences.** Completely unused. Each user has hundreds to thousands
   of train interactions. DIN / SIM-style interest modelling is untouched.
3. **Multi-task.** `is_click`, `is_like`, `is_follow`, `is_comment`, `is_forward`,
   `play_time_ms` as auxiliary tasks for the `long_view` main task.
4. **Watch-time modelling.** [CWM](https://github.com/hyz20/CWM) treats watch time as
   **censored regression** — true watch time is truncated when the video completes, so a
   one-sided loss beats squared error. Research-grade direction.
5. **Different architectures** — DeepFM / DCN / xDeepFM. Deprioritised below 1–4 because
   capacity is measured not to be the bottleneck.
6. **Temporal features and drift** — `hourmin`, `date`, and train→test distribution shift.
7. **Unbiased validation (advanced).** `log_random_4_22_to_5_08_pure.csv` is a random-
   exposure log of ~1.18M rows, usable as an extra unbiased validation set to check
   whether a model only works on biased traffic.

## 6. Submission format

```text
row_id,user_id,video_id,score
0,0,7531,-3.34176
```

`row_id` is 0-based and consecutive, matching the row order of `data.load()[split]`:
`log_standard_4_08_to_4_21_pure.csv` read first, then
`log_standard_4_22_to_5_08_pure.csv`, date-filtered, original file order preserved.

**Why `row_id` is mandatory:** `(user_id, video_id)` is **not unique** in the evaluation
set — 3.06% of test pairs repeat, up to 12 times. It cannot be a key.

`user_id` and `video_id` are redundant alignment-check fields. `score` is any real;
only relative order matters. NaN and Inf are rejected.

```bash
python3 submit.py --make  --split test  submission.csv
python3 submit.py --check --split test  submission.csv
python3 submit.py --score --split valid submission.csv
```

## 7. Using your own model

`evaluate.py` is fully decoupled from any model — it needs three equal-length arrays:

```python
from evaluate import evaluate
print(evaluate(user_ids, labels, scores))
```

So PyTorch, LightGBM, or anything else is fine. `evaluate.py` alone defines the score.

Note on CWM as a starting point: it depends on `torch==1.6.0` (a 2020 release, unlikely
to install on current GPUs), its loss optimises counterfactual watch time, and it
reconstructs its own `long_view2` label. Useful as an **advanced reference**, not as a
starting point.
