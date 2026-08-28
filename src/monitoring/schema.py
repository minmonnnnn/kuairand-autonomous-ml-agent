"""Resource accounting schema. Owner: Nandit. Status: SCAFFOLDED.

Resource accounting is a first-class feature, not end-of-project reporting. Feasibility
is 15% of the grade and autonomy is 20% — manual_interventions is a scored number.

NOT YET IMPLEMENTED: the collectors. See tasks T-502 and T-503.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass
class ResourceUsage:
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0

    agent_wall_clock_seconds: float = 0.0
    training_wall_clock_seconds: float = 0.0
    cpu_seconds: float = 0.0
    gpu_hours: float = 0.0
    peak_memory_mb: float = 0.0

    iterations: int = 0
    failures: int = 0
    retries: int = 0
    automatic_recoveries: int = 0
    manual_interventions: int = 0
    human_decision_points: int = 0

    @property
    def total_llm_tokens(self) -> int:
        return self.llm_input_tokens + self.llm_output_tokens

    def merge(self, other: ResourceUsage) -> ResourceUsage:
        out = ResourceUsage()
        for f in self.__dataclass_fields__:
            setattr(out, f, getattr(self, f) + getattr(other, f))
        out.peak_memory_mb = max(self.peak_memory_mb, other.peak_memory_mb)
        return out

    def to_json(self) -> str:
        d = asdict(self)
        d["total_llm_tokens"] = self.total_llm_tokens
        return json.dumps(d, indent=2)
