# Artifacts

| Directory | Contents | Owner |
|---|---|---|
| `checkpoints/` | Model checkpoints, referenced by experiment ID | Vidush |
| `metrics/` | Raw metric outputs per experiment | Sarthak |
| `submissions/` | Generated submission CSVs | Min |
| `reports/` | Final results report and resource report | Min / Sarthak |

Contents git-ignored, directories tracked.

Every checkpoint must be traceable to an experiment ID, config hash, feature version,
seed and git commit. A checkpoint without that provenance cannot be used for the final
submission because its result cannot be reproduced.
