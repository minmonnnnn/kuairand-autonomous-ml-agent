# Logs

Owner: Nandit. Contents git-ignored, directories tracked.

| Directory | Contents |
|---|---|
| `iterations/` | One structured JSON record per iteration (`src/logging/schema.py`) |
| `agent/` | Agent reasoning traces |
| `errors/` | Errors, recovery actions, and `split_access.log` (test-split audit trail) |
| `resources/` | Token, wall-clock, CPU, GPU and memory accounting |

Write the iteration record as the iteration ends, not at the end of the run — logs must
survive a crash, since crashes are exactly when they matter.
