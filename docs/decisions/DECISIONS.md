# Decision Log

Append-only. Record the reasoning, not just the verdict — the reasoning is what a
teammate needs six weeks later.

---

## D-001 · Preserve the starter kit verbatim

**Date:** 2026-08-28 · **Owner:** Min · **Status:** ACTIVE

The organizer code is reference, not a starting template. All adaptation happens in
`src/` via thin adapters (`src/data/loader.py`, `src/evaluation/official.py`). CI fails
any PR that modifies `starter_kit/`.

*Why:* if the loader drifts, submission row alignment breaks silently and is only caught
at the very end by `submit.py --check`. If the evaluator drifts, every number in the
project becomes incomparable, including against the published baseline.

*Alternative rejected:* forking the starter kit and editing it in place. Faster at first,
but destroys the ability to prove our numbers are computed the organizers' way.

---

## D-002 · One definition of the metrics

**Date:** 2026-08-28 · **Owner:** Sarthak · **Status:** ACTIVE

`starter_kit/evaluate.py` is imported, never copied, never reimplemented — not even
"equivalently" for speed. `src/evaluation/official.py` adds validation and a stable
import path, and no arithmetic.

*Why:* an equivalent-looking reimplementation is the classic way a leaderboard result
turns out to be unreproducible. The nDCG conventions here are unusual (zero-positive
users score 0 and stay in the average) and easy to get subtly wrong.

---

## D-003 · Ownership by directory, enforced by CODEOWNERS

**Date:** 2026-08-28 · **Owner:** Min · **Status:** ACTIVE

Each workstream owns directories, not features. GitHub auto-requests the owner's review
on any PR touching their paths.

*Why:* five people and one repository means merge conflicts are the default failure mode.
Directory ownership plus stable interfaces (C-01…C-08) lets four people rewrite their
internals in parallel without coordinating.

---

## D-004 · Significance floor of 0.0016 primary

**Date:** 2026-08-28 · **Owner:** Sarthak · **Status:** ACTIVE

Published FM seed std is 0.0008. A single-seed delta below 2σ is classified `NEUTRAL`,
never `IMPROVEMENT`. Accepting a change into the best-known configuration requires ≥3
seeds.

*Why:* with 50 iterations available, the cheapest way to waste the budget is to chase
noise and then build on top of a phantom gain. The convergence rule ε = 0.002 sits just
above this floor for the same reason.

---

## D-005 · Load the organizers' negative results as prior evidence

**Date:** 2026-08-28 · **Owner:** Min · **Status:** ACTIVE

The agent starts with `ORG-NEG-001/002/003` (static features, capacity, user-side
first-order terms) in `configs/agent/agent.yaml`, and the team has them in
`TEAM_SOT.md` §16.

*Why:* these are published, measured negatives. Spending iterations rediscovering them
is pure waste, and "adding more features" is the most natural first instinct for a team
of five — exactly the instinct that has already been tested and refuted here.

---

## D-006 · Test split behind an audited token

**Date:** 2026-08-28 · **Owner:** Min · **Status:** ACTIVE

`src/data/guard.py` requires an explicit `FinalSubmissionToken` to load test, and issuing
one writes to `logs/errors/split_access.log`.

*Why:* the test labels are physically on disk, so no technical barrier is possible. What
is possible is making test access **deliberate and auditable**, so accidental use cannot
happen quietly and intentional use leaves a record. Recorded honestly as `KI-001`.
