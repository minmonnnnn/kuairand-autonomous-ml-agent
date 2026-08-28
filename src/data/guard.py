"""Split access guard. Owner: Rishi (impl) / Min (policy). Status: IMPLEMENTED.

The test split is FINAL-ONLY. This module makes reading it require an explicit,
audited token, so that touching it is a deliberate act rather than an accident.

It is a guard rail, not a barrier: the test labels are on disk and anyone can read the
CSV directly. See KI-001 in TEAM_SOT.md and docs/runbooks/DATA_LEAKAGE_POLICY.md.
"""
from __future__ import annotations

import datetime as _dt
import json
from dataclasses import dataclass
from enum import Enum

from src.paths import ERROR_LOGS


class Split(str, Enum):
    TRAIN = "train"
    VALID = "valid"
    TEST = "test"


#: Access class per split, per the challenge specification.
SPLIT_CLASS = {
    Split.TRAIN: "DEVELOPMENT",
    Split.VALID: "VALIDATION",
    Split.TEST: "FINAL-ONLY",
}

DEV_SPLITS = (Split.TRAIN, Split.VALID)


class SplitAccessError(PermissionError):
    """Raised when FINAL-ONLY data is requested without a valid token."""


@dataclass(frozen=True)
class FinalSubmissionToken:
    """Explicit, audited authorisation to read the test split.

    Issued exactly once per final submission, from the submission workflow only.
    Issuing writes a line to logs/errors/split_access.log.
    """

    experiment_id: str
    reason: str
    issued_at: str

    @classmethod
    def issue(cls, experiment_id: str, reason: str) -> FinalSubmissionToken:
        token = cls(
            experiment_id=experiment_id,
            reason=reason,
            issued_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
        )
        ERROR_LOGS.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOGS / "split_access.log", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(token.__dict__) + "\n")
        return token


def check_access(split: Split, token: FinalSubmissionToken | None = None) -> None:
    """Raise SplitAccessError if this split may not be read right now."""
    if split in DEV_SPLITS:
        return
    if token is None:
        raise SplitAccessError(
            f"'{split.value}' is {SPLIT_CLASS[split]}. It may only be read by the final "
            "submission workflow, after the validation-best checkpoint is designated. "
            "Use FinalSubmissionToken.issue(...) if that is genuinely what you are "
            "doing. See docs/runbooks/DATA_LEAKAGE_POLICY.md."
        )
