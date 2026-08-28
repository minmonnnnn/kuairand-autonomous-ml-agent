# Team Roles

## The framing that matters

The five people are **not** one person per stage of the ML loop. There is no
"the person who does training" or "the person who does evaluation" in the sense of
running that stage by hand.

> **Five specialised engineering/research workstreams collectively build one autonomous
> system that performs the complete ML loop.**

The loop itself crosses all five workstreams:

```text
Data inspection          → Rishi's capability
Hypothesis generation    → Sarthak's capability + the agent
Feature modification     → Rishi's capability
Model modification       → Vidush's capability
Experiment execution     → Nandit's capability
Evaluation               → Sarthak's capability
Reflection               → Min + Sarthak + the agent
Integration              → Min
```

Nobody owns a loop *stage*. Everybody owns a *capability the loop calls into*.

---

## Min — System architecture, agent orchestration & integration

**Primary question:** How do we turn the team's capabilities into one autonomous ML
research system?

Owns: autonomous agent architecture · orchestration · experiment lifecycle ·
research-loop control flow · hypothesis→experiment→evaluation→reflection ·
experiment selection · configuration architecture · integration · final pipeline ·
final submission workflow · repository architecture · cross-team interfaces ·
single source of truth · reproducibility coordination.

Directories: `src/agent/`, `src/orchestration/`, `src/registry/`, `configs/`,
`docs/architecture/`, `docs/coordination/`, `docs/runbooks/`.

Does **not** independently own: Rishi's feature implementations, Vidush's model
implementations, Sarthak's evaluator internals, Nandit's runtime/recovery
implementations. Min integrates these rather than replacing them.

---

## Rishi — Data understanding & feature research

**Primary question:** What useful information exists in the allowed KuaiRand data that
the current pipeline fails to exploit?

Owns: data loading · schema understanding · EDA · feature inventory · data quality ·
leakage analysis · temporal features · user features · item/video features ·
interaction features · feature crosses · behavioural aggregates · preprocessing ·
feature versioning · feature ablations.

Directories: `src/data/`, `src/features/`, `experiments/features/`,
`docs/research/features/`, `tests/data/`, `tests/features/`.

Must expose stable interfaces so model code never depends on internal feature details.

**Read first:** the organizers already showed that adding *static* categorical features
gives no gain, and that pure user-side first-order terms are mathematically inert under
within-user ranking. Rishi's headroom is in **behavioural, sequential, temporal and
cross features** — not in wiring up more static columns.

---

## Vidush — Model & training research

**Primary question:** Given the available signals, what model and training strategy best
improves the evaluated ranking metrics?

Owns: model architectures · embeddings · FM-family approaches · DeepFM / Wide & Deep or
other justified architectures · multi-task learning · auxiliary feedback prediction ·
losses · optimisation · regularisation · hyperparameters · training loops ·
checkpointing · inference/scoring.

Directories: `src/models/`, `src/training/`, `experiments/models/`,
`docs/research/models/`, `tests/models/`, `tests/training/`.

Consumes stable feature interfaces; must not rewrite Rishi's feature pipeline.

**Read first:** embedding capacity is measured *not* to be the bottleneck. The highest-
value target in this workstream is the **loss function** — pointwise logloss is
misaligned with GAUC/nDCG. Architecture swaps are deprioritised.

---

## Sarthak — Evaluation, experimental science & research intelligence

**Primary question:** Which experiments are actually worth pursuing, and how do we know
whether an observed improvement is real?

Owns: official evaluator integration · GAUC analysis · nDCG@5 analysis · Primary
calculation · experiment comparison · ablation design · seed analysis · variance
analysis · convergence logic · statistical reasoning · literature review ·
public-solution analysis · hypothesis evaluation · research prioritisation.

Directories: `src/evaluation/`, `src/experiments/`, `src/research/`,
`experiments/analysis/`, `docs/research/`, `tests/evaluation/`.

Sarthak's work must actively influence future experiment selection — analysis that
does not change what gets tried next has failed at its job.

**Read first:** seed std is 0.0008. Sarthak is the gatekeeper who stops the team from
celebrating noise.

---

## Nandit — Runtime, robustness, recovery & resource efficiency

**Primary question:** How can the autonomous agent keep making progress when experiments
fail, time out, produce invalid outputs, or hit unexpected conditions?

Owns: subprocess management · experiment execution · timeout handling · retries ·
failure detection · rollback · checkpoint recovery · resource monitoring · LLM token
accounting · wall-clock accounting · GPU/CPU tracking · memory monitoring · run logging ·
robustness testing · execution safeguards.

Directories: `src/runtime/`, `src/reliability/`, `src/monitoring/`, `src/llm/`,
`src/logging/`, `tests/runtime/`, `tests/reliability/`, `docs/research/robustness/`.

**Read first:** resource accounting is 15% of the grade and autonomy is 20%. The
`manual_interventions` counter is a scored deliverable, not bookkeeping.

---

## The critical team rule

No teammate's agent may independently redefine the overall project strategy.

- Rishi should not independently replace the model architecture.
- Vidush should not rewrite the feature framework.
- Sarthak should not silently modify model implementations.
- Nandit should not redesign research methodology.
- Min should not bypass the specialists and duplicate their implementations.

Anyone may **propose** a cross-workstream change — via
`docs/coordination/change_requests/`.
