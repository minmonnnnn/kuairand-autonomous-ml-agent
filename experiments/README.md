# Experiments

One JSON record per experiment, named `EXP-NNNN.json`, schema in
`src/registry/schema.py` (contract C-08).

| Directory | Contents | Owner |
|---|---|---|
| `baseline/` | `EXP-0000-OFFICIAL-BASELINE` and reproduction evidence | Sarthak |
| `features/` | Feature experiments | Rishi |
| `models/` | Model, loss and training experiments | Vidush |
| `ablations/` | Controlled removals | Sarthak |
| `analysis/` | Cross-experiment comparisons, seed variance, segment analysis | Sarthak |
| `archived/` | Superseded records — kept, never deleted | Sarthak |

**Records are never deleted.** A failed or rejected experiment is research evidence and
is explicitly graded. Superseding a record means moving it to `archived/` and setting
`superseded_by`, not removing it.
