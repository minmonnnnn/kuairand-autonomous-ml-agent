"""Experiment record schema. Owner: Min. Status: IMPLEMENTED. Contract: C-08.

Records are append-only JSON. They are never deleted — a failed experiment is research
evidence and is graded as such.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


class ExperimentStatus:
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    INVALID = "INVALID"
    REJECTED = "REJECTED"
    VALIDATED = "VALIDATED"
    SUPERSEDED = "SUPERSEDED"

    ALL = (
        PLANNED, RUNNING, SUCCESS, FAILED, TIMEOUT,
        INVALID, REJECTED, VALIDATED, SUPERSEDED,
    )


@dataclass
class ExperimentRecord:
    """One experiment. Fields mirror the specification in the master README."""

    experiment_id: str
    owner: str
    hypothesis_id: str | None = None
    parent_experiment: str | None = None
    timestamp: str | None = None
    research_area: str | None = None

    hypothesis: str | None = None
    motivation: str | None = None
    changes: list[str] = field(default_factory=list)

    config: dict[str, Any] = field(default_factory=dict)
    config_hash: str | None = None
    dataset: str = "KuaiRand-Pure"
    split: str = "valid"
    feature_version: str | None = None
    model: str | None = None
    training: dict[str, Any] = field(default_factory=dict)
    seed: int | None = None
    seeds: list[int] = field(default_factory=list)

    status: str = ExperimentStatus.PLANNED

    validation_gauc: float | None = None
    validation_ndcg5: float | None = None
    validation_primary: float | None = None
    validation_primary_std: float | None = None
    delta_vs_official_baseline: float | None = None
    delta_vs_previous: float | None = None
    significant: bool | None = None

    wall_clock_seconds: float | None = None
    gpu_hours: float = 0.0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    manual_interventions: int = 0
    errors: list[dict] = field(default_factory=list)
    recovery_actions: list[dict] = field(default_factory=list)

    checkpoint: str | None = None
    git_commit: str | None = None
    artifacts: dict[str, str] = field(default_factory=dict)

    is_validation_best: bool = False
    is_converged: bool = False
    superseded_by: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.status not in ExperimentStatus.ALL:
            raise ValueError(f"unknown status {self.status!r}")
        if self.validation_primary is not None:
            g, n = self.validation_gauc, self.validation_ndcg5
            if g is not None and n is not None:
                expected = (g + n) / 2.0
                if abs(expected - self.validation_primary) > 1e-6:
                    raise ValueError(
                        "validation_primary must equal mean(GAUC, nDCG@5); "
                        f"got {self.validation_primary} vs {expected}"
                    )

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=False)

    @classmethod
    def from_dict(cls, d: dict) -> ExperimentRecord:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})
