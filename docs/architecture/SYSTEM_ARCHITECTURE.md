# System Architecture

Status: `SCAFFOLDED` · Owner: Min

## 1. What the system is

One autonomous ML research agent that improves a recommender pipeline on KuaiRand-Pure
and leaves an auditable trail of what it tried, why, what happened, how it recovered,
and what it cost.

It is not a model. The model is an output of the system.

## 2. Layers

```text
┌──────────────────────────────────────────────────────────────────┐
│  AGENT LAYER                                        (Min)        │
│  problem analyzer · researcher · planner · coder                 │
│  critic/reflector · experiment selector                          │
└───────────────────────────┬──────────────────────────────────────┘
                            │ ExperimentSpec (C-06)
┌───────────────────────────▼──────────────────────────────────────┐
│  ORCHESTRATION LAYER                                (Min)        │
│  config resolution · experiment lifecycle · registry             │
│  convergence gate · checkpoint policy · submission workflow      │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│  RUNTIME LAYER                                      (Nandit)     │
│  subprocess execution · timeout · retry · failure detection      │
│  recovery · rollback · resource + token accounting · run logs    │
└───────────────────────────┬──────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────────┐
│ DATA+FEATURES │   │ MODEL+TRAINING│   │ EVALUATION        │
│    (Rishi)    │──▶│   (Vidush)    │──▶│   (Sarthak)       │
│ FeatureBundle │   │ TrainingResult│   │ EvaluationSummary │
│     (C-02)    │   │     (C-03)    │   │   (C-04, C-05)    │
└───────────────┘   └───────────────┘   └─────────┬─────────┘
                                                  │
                                                  ▼
                                        back to the agent's
                                        critic + selector
```

## 3. Why it is layered this way

**The agent never touches data or models directly.** It emits an `ExperimentSpec` and
receives a `RunResult` plus an `EvaluationSummary`. This means the agent can be tested
with stub components, and the specialists can rewrite their internals freely.

**The runtime is a separate layer from the orchestration.** Orchestration decides *what*
to run; runtime decides *how to survive running it*. Mixing them is why autonomous
systems tend to hang on the first unexpected exception.

**Evaluation is a leaf, never a dependency of training.** Training may compute
validation metrics for early stopping, but the authoritative number always comes from
the same adapter over `starter_kit/evaluate.py`. There is exactly one definition of the
score in this repository.

## 4. Reproducibility contract

Every recorded experiment carries: git commit · resolved-config hash · feature version ·
seed · dataset split identity · checkpoint path. Re-running with those five things must
reproduce the metrics.

## 5. Leakage containment

The test split is reachable through exactly one code path (`src/data/guard.py`), which
requires an explicit final-submission token. Every other entry point can physically only
see train and valid. This is a guard rail, not a proof — the labels are on disk, so the
policy in `docs/runbooks/DATA_LEAKAGE_POLICY.md` is what ultimately holds.

## 6. What is real today

| Layer | Status |
|---|---|
| Evaluation adapter | `IMPLEMENTED` + tested |
| Data adapter + split guard | `IMPLEMENTED` |
| Experiment registry | `IMPLEMENTED` + tested |
| Convergence tracker | `IMPLEMENTED` + tested |
| Feature framework | `SCAFFOLDED` — ABC only |
| Model framework | `SCAFFOLDED` — ABC only |
| Training loop | `PLANNED` |
| Agent layer | `SCAFFOLDED` — control flow, no LLM calls |
| Runtime layer | `PLANNED` |
| Resource accounting | `SCAFFOLDED` — schema only |
