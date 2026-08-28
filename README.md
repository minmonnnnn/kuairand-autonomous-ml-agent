# KuaiRand Autonomous ML Research Agent

An autonomous ML research agent for the **KuaiRand-Pure** within-user ranking challenge.
The system is designed to run the full research cycle on its own — read the problem,
inspect data, engineer features, train, evaluate, reflect, choose the next experiment,
repeat until convergence — while producing an auditable record of everything it tried.

> **Repository status: MILESTONE 0 — FOUNDATION.**
> The structure, contracts, coordination system and experiment infrastructure exist.
> The autonomous loop is **scaffolded, not implemented**. No experimental results have
> been produced yet. See [`TEAM_SOT.md`](TEAM_SOT.md) for live state.

---

## 1. The challenge in one screen

| | |
|---|---|
| Task | Within-user ranking over logged impressions (**not** full-catalog retrieval) |
| Dataset | KuaiRand-Pure (required). KuaiRand-1K / 27K are optional bonus. |
| Label | `long_view` (native column, 0/1) |
| Metrics | GAUC, nDCG@5 |
| **Primary** | `mean(GAUC, nDCG@5)` |
| Train | `20220408–20220421` — 1,141,112 rows |
| Validation | `20220422–20220428` — 124,909 rows |
| Hidden test | `20220429–20220508` — 170,588 rows |
| Convergence | `epsilon = 0.002`, `N = 3` |
| Run limits | 50 iterations **or** 6 hours wall-clock |

### The bar to beat

| | GAUC | nDCG@5 | Primary |
|---|---:|---:|---:|
| Random (sanity lower bound) | 0.4996 | 0.4511 | 0.4753 |
| Item popularity (trivial) | 0.6308 | 0.5121 | 0.5715 |
| **FM — official baseline (test)** | **0.6610** | **0.5282** | **0.5946** |
| FM — official baseline (valid) | 0.6674 | 0.5357 | 0.6016 |
| **Oracle ceiling (test)** | 1.0000 | **0.7289** | **0.8645** |

### Read the ceiling before you set a target

nDCG@5 **cannot reach 1.0**. On the test split, 27.1% of users are all-negative
(nDCG is permanently 0 for them) and 9.2% are all-positive (permanently 1). Only 63.7%
of users are discriminative, and only those count toward GAUC.

The official FM has already captured **30.7%** of the usable range. Remaining headroom
is **0.27 Primary, not 0.41**. Measure progress against the oracle, not against 1.0.

Seed noise: FM's Primary has std **0.0008** across 5 seeds. A movement under
**±0.0016 (2σ)** is not a result. This is why `epsilon = 0.002`.

---

## 2. Where the headroom actually is

The organizers ran two ablations and published the outcome. **Do not spend iterations
rediscovering these:**

| Already tested by organizers | Result |
|---|---|
| Adding static features (all 13 CWM fields: `music_id`, `video_type`, `upload_type`, + 6 user-side buckets) | Primary 0.5940 vs 0.5950 for 5 fields — inside noise, if anything slightly worse |
| Adding model capacity (embedding `k` = 8 / 16 / 32) | 0.5895 / 0.5902 / 0.5887 — essentially flat |

Why: the `user_id × video_id` cross already absorbs most of the learnable signal, and
1.14M rows will not support more capacity. **The bottleneck is neither features nor capacity.**

Also note: **pure user-side first-order terms contribute exactly zero.** Ranking happens
within a user, so any term constant within a user cannot change the within-user order.
User-side features can only act through **crosses with item-side features**.

Unexplored directions, in the organizers' order of expected payoff:

1. **Change the loss.** Training is pointwise logloss; the metrics are ranking metrics.
   Pairwise (BPR) or listwise (softmax over the user's impressions) aligns the objective
   with the evaluation. Judged most likely to work.
2. **User behaviour sequences.** Currently unused entirely. Hundreds to thousands of
   interactions per user exist in train. DIN / SIM-style interest modelling is untouched.
3. **Multi-task.** `is_click`, `is_like`, `is_follow`, `is_comment`, `is_forward`,
   `play_time_ms` are all available as auxiliary tasks for the `long_view` main task.
4. **Watch-time modelling.** Censored regression on watch time (CWM's contribution —
   watch time is truncated when a video completes, so use a one-sided loss).
5. **Different architectures** (DeepFM / DCN / xDeepFM). Deprioritised — capacity is
   measured not to be the bottleneck.
6. **Temporal features and distribution drift** (`hourmin`, `date`, train→test drift).
7. **Unbiased validation (advanced).** `log_random_4_22_to_5_08_pure.csv` is a random-
   exposure log (1.18M rows), usable as an extra unbiased validation set.

Full digest: [`docs/research/STARTER_KIT_NOTES.md`](docs/research/STARTER_KIT_NOTES.md).

---

## 3. Quickstart

```bash
git clone <REPO_URL> && cd kuairand-autonomous-ml-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Download the dataset (~not committed, git-ignored)
wget https://zenodo.org/records/10439422/files/KuaiRand-Pure.tar.gz
tar xzf KuaiRand-Pure.tar.gz

# Reproduce the official baseline (~40s, single CPU core)
bash scripts/baseline/run_official_baseline.sh

# Sanity-check the evaluation harness — must give Primary ~0.475 (+/-0.001)
cd starter_kit && python3 baseline.py --model random --data_dir ../KuaiRand-Pure/data
```

Full setup: [`docs/runbooks/LOCAL_SETUP.md`](docs/runbooks/LOCAL_SETUP.md).
Baseline protocol: [`docs/runbooks/BASELINE_REPRODUCTION.md`](docs/runbooks/BASELINE_REPRODUCTION.md).

---

## 4. Team

Five **specialised engineering workstreams** that collectively build **one** autonomous
system. This is deliberately *not* one person per stage of the ML loop.

| Person | Workstream | Branch | Primary directories |
|---|---|---|---|
| **Min** | System architecture, agent orchestration, integration | `min/architecture` | `src/agent/`, `src/orchestration/`, `src/registry/`, `configs/`, `docs/` |
| **Rishi** | Data understanding & feature research | `rishi/features` | `src/data/`, `src/features/` |
| **Vidush** | Model & training research | `vidush/models` | `src/models/`, `src/training/` |
| **Sarthak** | Evaluation, experimental science, research intelligence | `sarthak/evaluation` | `src/evaluation/`, `src/experiments/`, `src/research/` |
| **Nandit** | Runtime, robustness, recovery, resource efficiency | `nandit/runtime` | `src/runtime/`, `src/reliability/`, `src/monitoring/`, `src/llm/`, `src/logging/` |

Enforced mechanically by [`.github/CODEOWNERS`](.github/CODEOWNERS).
Details: [`docs/coordination/TEAM_ROLES.md`](docs/coordination/TEAM_ROLES.md),
[`docs/coordination/OWNERSHIP_MATRIX.md`](docs/coordination/OWNERSHIP_MATRIX.md).

---

## 5. Start here as a new contributor

Read in this order:

1. [`TEAM_SOT.md`](TEAM_SOT.md) — current state of everything
2. [`docs/coordination/TEAM_ROLES.md`](docs/coordination/TEAM_ROLES.md) — what you own
3. [`docs/coordination/OWNERSHIP_MATRIX.md`](docs/coordination/OWNERSHIP_MATRIX.md) — what you must not touch
4. [`docs/coordination/INTERFACE_CONTRACTS.md`](docs/coordination/INTERFACE_CONTRACTS.md) — how your code talks to everyone else's
5. [`docs/coordination/TASK_BOARD.md`](docs/coordination/TASK_BOARD.md) — your next task
6. [`CONTRIBUTING.md`](CONTRIBUTING.md) — branch, commit, PR rules

---

## 6. Non-negotiable rules

- **The hidden test split is off-limits during development.** No tuning, feature
  selection, model selection, convergence decisions or debugging against test labels.
  See [`docs/runbooks/DATA_LEAKAGE_POLICY.md`](docs/runbooks/DATA_LEAKAGE_POLICY.md).
- **`starter_kit/` is organizer reference code. Never edit it.** Adapters live in `src/`.
  See [`starter_kit/PRESERVED.md`](starter_kit/PRESERVED.md).
- **`starter_kit/evaluate.py` is the only definition of the metrics.** Never reimplement.
- **No external training data.** Papers, libraries, public solutions and pretrained
  weights are allowed; extra training data is not.
- **Never delete a failed experiment.** Failures are research evidence.
- **Never describe scaffolding as implementation.** Use the status vocabulary:
  `PLANNED` / `SCAFFOLDED` / `IMPLEMENTED` / `TESTED` / `VALIDATED`.

---

## 7. Repository map

```text
configs/       run + experiment configuration           (Min)
docs/          architecture, coordination, runbooks, research
src/           all implementation, split by workstream
tests/         unit / integration / failure tests
experiments/   per-experiment records and analysis
research/      papers, public solutions, hypothesis queue
runs/          active / completed / failed agent runs
logs/          iteration, agent, error, resource logs
artifacts/     checkpoints, metrics, submissions, reports
scripts/       thin CLI entry points
starter_kit/   ORGANIZER REFERENCE — READ ONLY
notebooks/     exploration (never on the reproduction path)
```

## 8. Judging criteria this repo is built to satisfy

| Criterion | Weight | Where it lives |
|---|---:|---|
| Technical Execution | 35% | baseline reproduction, end-to-end run, recovery, checkpoints |
| Innovation & Problem Insight | 20% | `research/`, `docs/research/hypotheses/` |
| Impact & Relevance (autonomy) | 20% | `manual_interventions` / `human_decision_points` tracking |
| Feasibility & Practicality | 15% | `src/monitoring/`, `src/llm/` resource accounting |
| Presentation & Communication | 10% | `docs/`, final report in `artifacts/reports/` |
