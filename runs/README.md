# Runs

Owner: Nandit.

| Directory | Contents |
|---|---|
| `active/` | The run currently executing |
| `completed/` | Runs that reached a terminal state: `CONVERGED`, `MAX_ITERATIONS`, `TIMEOUT` |
| `failed/` | Runs that died unexpectedly — **kept, not deleted** |

Contents are git-ignored; the directories are tracked. A failed run's directory is
evidence for the robustness story and must survive.
