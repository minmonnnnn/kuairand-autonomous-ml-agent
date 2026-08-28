# Rejected Directions

Rejected on the organizers' published evidence, before we ran anything:

| ID | Direction | Evidence |
|---|---|---|
| `ORG-NEG-001` | Adding static categorical features (CWM's 13 fields) | primary 0.5940 vs 0.5950 — within noise |
| `ORG-NEG-002` | Increasing embedding dimension (k = 8/16/32) | 0.5895 / 0.5902 / 0.5887 — flat |
| `ORG-NEG-003` | Pure user-side first-order features | constant within a user, so mathematically inert under within-user ranking |

Reviving any of these requires a documented reason here plus a change request. A
legitimate reason exists — for example, static features may behave differently under a
listwise objective than they did under pointwise logloss — but it must be argued, not
assumed.
