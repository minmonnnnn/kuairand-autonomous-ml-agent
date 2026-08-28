"""Append-only experiment registry. Owner: Min. Status: IMPLEMENTED. Contract: C-08."""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.paths import EXPERIMENTS
from src.registry.schema import ExperimentRecord, ExperimentStatus

#: Baselines and rejected results still count as records, so a numeric scan is safest.
_ID_RE = re.compile(r"^EXP-(\d{4})")

#: Official organizer baseline, validation split. Used for delta computation.
OFFICIAL_BASELINE_VALID_PRIMARY = 0.6016

#: Statuses whose metrics may be considered for validation-best.
_ELIGIBLE = (ExperimentStatus.SUCCESS, ExperimentStatus.VALIDATED)


class DuplicateExperimentId(ValueError):
    """An experiment ID was reused. IDs are immutable and never recycled."""


class ExperimentRegistry:
    """JSON-file-backed registry over experiments/<area>/EXP-NNNN.json."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root or EXPERIMENTS)

    # ---------- reading ----------

    def paths(self) -> list[Path]:
        return sorted(p for p in self.root.rglob("EXP-*.json") if p.is_file())

    def all(self) -> list[ExperimentRecord]:
        out = []
        for p in self.paths():
            with open(p, encoding="utf-8") as fh:
                out.append(ExperimentRecord.from_dict(json.load(fh)))
        return out

    def get(self, experiment_id: str) -> ExperimentRecord | None:
        for r in self.all():
            if r.experiment_id == experiment_id:
                return r
        return None

    def next_id(self) -> str:
        n = 0
        for p in self.paths():
            m = _ID_RE.match(p.stem)
            if m:
                n = max(n, int(m.group(1)))
        return f"EXP-{n + 1:04d}"

    # ---------- writing ----------

    def save(self, record: ExperimentRecord, area: str = "models") -> Path:
        """Write a record. Refuses to create a duplicate ID under a different path."""
        target_dir = self.root / area
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{record.experiment_id}.json"

        for p in self.paths():
            if p.stem == record.experiment_id and p != target:
                raise DuplicateExperimentId(
                    f"{record.experiment_id} already exists at {p}. IDs are immutable."
                )

        if record.validation_primary is not None and record.delta_vs_official_baseline is None:
            record.delta_vs_official_baseline = (
                record.validation_primary - OFFICIAL_BASELINE_VALID_PRIMARY
            )

        target.write_text(record.to_json(), encoding="utf-8")
        self.refresh_validation_best()
        return target

    # ---------- derived state ----------

    def validation_best(self) -> ExperimentRecord | None:
        """The eligible record with the highest validation primary.

        Never assume the latest experiment is the best one — that is exactly the
        mistake this method exists to prevent.
        """
        candidates = [
            r for r in self.all()
            if r.status in _ELIGIBLE and r.validation_primary is not None
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.validation_primary)

    def refresh_validation_best(self) -> None:
        """Recompute is_validation_best across every record. Never set by hand."""
        best = self.validation_best()
        best_id = best.experiment_id if best else None
        for p in self.paths():
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
            want = d.get("experiment_id") == best_id
            if d.get("is_validation_best") != want:
                d["is_validation_best"] = want
                p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def next_experiment_id(root: Path | None = None) -> str:
    return ExperimentRegistry(root).next_id()
