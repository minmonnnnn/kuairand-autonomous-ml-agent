# H-001 · Ranking-loss alignment

```text
HYPOTHESIS ID:  H-001
Owner:          Vidush (implementation), Sarthak (analysis)
Date:           2026-08-28
Research area:  objective
Status:         QUEUED — nothing has been run
Priority:       P0 — highest-expected-value unexplored direction
```

**Problem**

The official FM trains with pointwise logistic loss, but the challenge scores GAUC and
nDCG@5, both of which depend only on the *ordering* of a user's impressions. Pointwise
training spends capacity on calibrating absolute probabilities that the metric ignores.

**Observation**

The organizers name this as the most promising unexplored direction in
`starter_kit/README.md`. They also established that neither more features nor more
capacity helps, which makes objective misalignment the leading remaining suspect.

**Hypothesis**

Replacing the pointwise logloss with a within-user pairwise (BPR) or listwise (softmax
over the user's impressions) objective improves validation primary, at unchanged feature
set and model capacity.

**Mechanism**

Pairwise/listwise losses only receive gradient from *relative* comparisons inside a
user's impression list. That is precisely the quantity GAUC measures and nDCG@5 rewards.
A pointwise loss, by contrast, is dominated by matching the global positive rate, which
is invariant to within-user permutation — so much of its gradient is orthogonal to the
metric.

This also predicts a specific asymmetry: the gain should concentrate in the 63.7% of
users who are discriminative, since all-positive and all-negative users cannot change.

**Expected effect**

Positive on GAUC, positive but smaller on nDCG@5. Magnitude unknown; anything below
0.0016 primary is not a result.

**Risk**

- Pairwise sampling adds a hyperparameter (pairs per user) that could dominate the effect
- Users with a single impression contribute no pairs and are silently dropped from
  training — this must be measured, not assumed harmless
- Listwise softmax over highly variable list lengths may need length normalisation

**Experiment**

Parent: `EXP-0000-OFFICIAL-BASELINE`. Same 5 fields, same k=16, same optimiser. Change
only the loss. Two arms:

- `EXP-000A` BPR pairwise, sampled within-user positive/negative pairs
- `EXP-000B` listwise softmax cross-entropy over each user's impressions

**Success criterion**

Mean valid primary improvement > 0.0016 over seeds 0, 1, 2, with non-overlapping std.

**Failure criterion**

No arm clears the floor over 3 seeds. Then objective misalignment is not the bottleneck
and priority moves to H-002 (behaviour sequences).

**Follow-up**

If it works: combine with sequence features (H-002) and test whether the gains are
additive or overlapping. If it fails: record it prominently — a negative result on the
organizers' top-ranked suggestion is genuinely informative and worth reporting.
