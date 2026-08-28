# Handoff Template

Copy this into your PR description or into `docs/coordination/handoffs/` when pausing
work. The test: **a teammate who has never spoken to you can pick this up.** No critical
knowledge should live only in a DM or in someone's head.

```text
Owner:
Workstream:
Date:

Completed:
  - what actually works, with status (IMPLEMENTED / TESTED / VALIDATED)

In progress:
  - what is half-done, and where exactly it stops

Files changed:
  - path — what changed and why

Interfaces changed:
  - contract ID + version, or "none"

Tests:
  - what passes, what is missing, how to run them

Known limitations:
  - what will bite the next person

Artifacts:
  - experiment IDs, checkpoints, run logs, metric files produced

Metrics produced:
  - experiment ID, seeds, valid GAUC / nDCG@5 / primary, or "none"

Next action:
  - the single next thing to do

Blocked by:
  - person, decision, or dependency; or "nothing"

Required reviewer:
```

## Handoff hygiene

- Never hand off with uncommitted work.
- Never hand off with an unrecorded experiment. If you ran it, register it.
- If you produced a number, say which seed and which split produced it.
- If something is broken, say so plainly. Hidden breakage costs more than admitted
  breakage.
