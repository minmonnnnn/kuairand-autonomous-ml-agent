# Hypothesis Template

Every non-trivial experiment needs one. Copy to `H-NNN-slug.md` in
`research/hypothesis_queue/`.

```text
HYPOTHESIS ID:
Owner:
Date:
Research area:      data | features | model | objective | training | evaluation | robustness

Problem:
    What is currently limiting the metric?

Observation:
    What evidence points at this? Cite an experiment ID, an EDA finding, or a paper.

Hypothesis:
    A single falsifiable claim.

Mechanism:
    WHY would this change the within-user ordering? This field catches most bad ideas.
    Remember: anything constant within a user cannot change that user's ranking.

Expected effect:
    Direction and rough magnitude on GAUC and/or nDCG@5. "Improves primary" is not an
    answer; the noise floor is 0.0016.

Risk:
    Overfitting, leakage, compute cost, implementation complexity.

Experiment:
    Change exactly one thing. Name the parent experiment.

Success criterion:
    Must clear 0.0016 valid primary over >= 3 seeds.

Failure criterion:
    What result would make you abandon this line?

Follow-up:
    What does each outcome unlock?
```

## Before submitting

- [ ] Checked against the rejected list in `TEAM_SOT.md` §16
- [ ] The mechanism section survives the within-user-ranking argument
- [ ] Exactly one variable changes
- [ ] The parent experiment is named
