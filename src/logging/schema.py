"""Iteration log schema. Owner: Nandit. Status: SCAFFOLDED.

One structured record per iteration, written to logs/iterations/. Must survive a
crashed run — write it as the iteration ends, not at the end of the whole run.

NOT YET IMPLEMENTED: the writer itself. See task T-501.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field


@dataclass
class IterationLog:
    iteration: int
    experiment_id: str
    hypothesis_id: str | None = None
    parent_experiment: str | None = None
    owner: str | None = None
    hypothesis: str = ""
    changes: list[str] = field(default_factory=list)

    validation: dict = field(default_factory=lambda: {"gauc": None, "ndcg5": None, "primary": None})
    delta_vs_official_baseline: float | None = None
    delta_vs_previous: float | None = None
    status: str = "pending"

    manual_interventions: int = 0
    errors: list[dict] = field(default_factory=list)
    recovery_actions: list[dict] = field(default_factory=list)

    wall_clock_seconds: float = 0.0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    gpu_hours: float = 0.0

    checkpoint: str | None = None
    git_commit: str | None = None
    notes: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
