# Agent Architecture

Status: `SCAFFOLDED` · Owner: Min

## Components

| Component | Produces | Notes |
|---|---|---|
| Problem Analyzer | task understanding, constraints, metric targets, baseline targets | Runs once. Its output is essentially `TEAM_SOT.md` §2–§5. |
| Data Analyst | EDA, feature inventory, anomalies, leakage risks, candidate hypotheses | Calls Rishi's capability. Train + valid only. |
| Researcher | research-backed hypotheses | Draws on `research/papers/`, `research/public_solutions/` |
| Experiment Planner | a concrete `ExperimentSpec` | Must name a parent experiment and a hypothesis ID |
| Coding Agent | controlled code changes | Smallest coherent diff; one variable at a time |
| Runner | `RunResult` | Nandit's layer. Never interprets metrics. |
| Evaluator | GAUC, nDCG@5, Primary, diagnostics | Sarthak's adapter over the official evaluator |
| Critic / Reflector | interpretation, failure analysis, next-step recommendation | Must distinguish "no effect" from "noise" |
| Experiment Selector | the next experiment | Reasons over history, not just the last result |
| Recovery Manager | retry / patch / rollback / alternate route | Every escalation costs autonomy score |
| Resource Monitor | tokens, wall-clock, CPU, GPU, memory, interventions | Always on |

## Control flow

```text
Problem Understanding
        ↓
Data Inspection
        ↓
Baseline Verification  ← gate: nothing proceeds until EXP-0000 is VALIDATED
        ↓
Research / Hypothesis Generation
        ↓
Experiment Planning
        ↓
Code Modification
        ↓
Training  ──── failure ───▶ Recovery Manager ───┐
        ↓                                        │
Evaluation                                       │
        ↓                                        │
Result Analysis                                  │
        ↓                                        │
Reflection                                       │
        ↓                                        │
Decision                                         │
   ↙         ↘                                   │
KEEP        REJECT                               │
   ↓           ↓                                 │
Registry update (both are recorded)  ◀───────────┘
        ↓
Next experiment selection
        ↓
Convergence check ──▶ CONVERGED / MAX_ITERATIONS / TIMEOUT
        ↓
Validation-best checkpoint designation
        ↓
Final submission
```

## Design commitments

**The agent does not chase the last score.** Selection reasons over the full experiment
history: expected improvement, implementation cost, compute cost, uncertainty, evidence
from related experiments, novelty, leakage risk, compatibility with the current best,
previous failures, and remaining budget.

**The agent knows what is already ruled out.** The organizer-published negative results
(static features, embedding capacity) are loaded as prior evidence at start-up. Burning
iterations rediscovering them is a failure mode we can cheaply prevent.

**The agent respects the noise floor.** With seed std 0.0008, a single-seed gain of
0.001 is nothing. The critic must treat sub-2σ movements as `NEUTRAL` and demand
multi-seed confirmation before accepting a change into the best-known configuration.

**Budget awareness is explicit.** 50 iterations and 6 hours. Spending 20 iterations on
variations of one idea without evidence is a planning failure, and the selector is
responsible for preventing it.

## Not yet built

Every component above is currently an interface with a stub. No LLM calls are wired.
See `T-104` on the task board.
