## What and why

<!-- One paragraph. Link the task ID (T-NNN) and hypothesis ID (H-NNN) if applicable. -->

## Workstream

<!-- Min / Rishi / Vidush / Sarthak / Nandit -->

## Status of this change

<!-- Pick one, honestly. Do not describe scaffolding as implementation. -->

- [ ] `SCAFFOLDED` — interface exists, does not do the job yet
- [ ] `IMPLEMENTED` — works
- [ ] `TESTED` — has passing automated tests
- [ ] `VALIDATED` — verified against the challenge's own criteria

## Ownership check

- [ ] Every file I touched is one I own (`docs/coordination/OWNERSHIP_MATRIX.md`)
- [ ] I did not modify `starter_kit/` (`git diff --stat starter_kit/` is empty)
- [ ] I did not reimplement the metrics

## Interfaces

- [ ] No interface changed
- [ ] An interface changed — change request: CR-____ , contracts updated, consumers updated in this PR

## Data policy

- [ ] No test-split data influenced anything in this PR
- [ ] Model/feature selection used validation primary only

## Results (if this PR produces numbers)

| Experiment | Seeds | Valid GAUC | Valid nDCG@5 | Valid Primary | Δ vs parent |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

- [ ] Δ exceeds the 2σ floor of **0.0016**, over ≥3 seeds — or is explicitly labelled `NEUTRAL`
- [ ] The experiment is recorded in `experiments/`, including if it failed

## Testing

<!-- What you ran. `pytest -q` output, or why tests were not applicable. -->

## SOT

- [ ] I updated my rows in `TEAM_SOT.md` in this PR
