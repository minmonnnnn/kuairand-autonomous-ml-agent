# Ownership Matrix

The purpose of this document is **minimum merge conflicts**. If two people are editing
the same file regularly, that is a design problem — raise a change request.

`O` = owner (writes freely) · `C` = consumer (reads, may not edit) ·
`R` = review required · `—` = not involved

## Source directories

| Path | Min | Rishi | Vidush | Sarthak | Nandit |
|---|:--:|:--:|:--:|:--:|:--:|
| `src/agent/` | **O** | C | C | C | C |
| `src/orchestration/` | **O** | C | C | C | C |
| `src/registry/` | **O** | C | C | C | C |
| `src/paths.py` | **O** | C | C | C | C |
| `src/data/` | R | **O** | C | C | — |
| `src/features/` | R | **O** | C | C | — |
| `src/models/` | R | C | **O** | C | — |
| `src/training/` | R | C | **O** | C | C |
| `src/evaluation/` | R | C | C | **O** | — |
| `src/experiments/` | R | C | C | **O** | C |
| `src/research/` | R | C | C | **O** | — |
| `src/runtime/` | R | — | C | — | **O** |
| `src/reliability/` | R | — | — | — | **O** |
| `src/monitoring/` | R | — | — | C | **O** |
| `src/llm/` | R | — | — | — | **O** |
| `src/logging/` | R | C | C | C | **O** |

## Config, docs, tests, artifacts

| Path | Min | Rishi | Vidush | Sarthak | Nandit |
|---|:--:|:--:|:--:|:--:|:--:|
| `configs/base.yaml` | **O** | R | R | R | R |
| `configs/baseline.yaml` | **O** | — | — | R | — |
| `configs/features/` | C | **O** | C | C | — |
| `configs/models/` | C | C | **O** | C | — |
| `configs/agent/` | **O** | — | — | C | C |
| `configs/experiments/` | **O** | C | C | C | C |
| `docs/architecture/` | **O** | C | C | C | C |
| `docs/coordination/` | **O** | C | C | C | C |
| `docs/runbooks/` | **O** | C | C | R | R |
| `docs/decisions/` | **O** | C | C | C | C |
| `docs/research/features/` | C | **O** | C | C | — |
| `docs/research/models/` | C | C | **O** | C | — |
| `docs/research/evaluation/` | C | C | C | **O** | — |
| `docs/research/robustness/` | C | — | — | C | **O** |
| `docs/research/literature/` | C | C | C | **O** | C |
| `docs/research/hypotheses/` | C | C | C | **O** | C |
| `research/` | C | C | C | **O** | C |
| `tests/data/`, `tests/features/` | R | **O** | — | — | — |
| `tests/models/`, `tests/training/` | R | — | **O** | — | — |
| `tests/evaluation/` | R | — | — | **O** | — |
| `tests/runtime/`, `tests/reliability/` | R | — | — | — | **O** |
| `tests/unit/`, `tests/integration/` | **O** | C | C | C | C |
| `experiments/features/` | C | **O** | — | C | — |
| `experiments/models/` | C | — | **O** | C | — |
| `experiments/analysis/`, `experiments/ablations/` | C | C | C | **O** | — |
| `experiments/baseline/` | R | — | — | **O** | — |
| `runs/`, `logs/` | C | C | C | C | **O** |
| `artifacts/checkpoints/` | C | — | **O** | C | C |
| `artifacts/submissions/` | **O** | — | — | R | — |
| `artifacts/reports/` | **O** | C | C | **O** | C |
| `scripts/` | **O** | C | C | C | C |
| `notebooks/` | — | O | O | O | O (own subfolder) |

## Shared files — change request required

Editing any of these needs a change request and Min's approval:

```text
TEAM_SOT.md                 (exception: everyone updates their own rows)
README.md
CONTRIBUTING.md
pyproject.toml
requirements.txt
configs/base.yaml
docs/coordination/INTERFACE_CONTRACTS.md
.github/CODEOWNERS
```

## Read-only for everyone

```text
starter_kit/**              organizer reference code — NEVER edit
LICENSE
```

## Enforcement

`.github/CODEOWNERS` maps these rules onto GitHub review requirements. If a PR touches
a path you do not own, GitHub will request the owner's review automatically.
