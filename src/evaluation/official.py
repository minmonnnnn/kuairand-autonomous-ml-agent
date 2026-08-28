"""Thin adapter over the organizer's evaluator. Owner: Sarthak. Status: IMPLEMENTED.

This module deliberately contains no metric arithmetic. `starter_kit/evaluate.py` is the
single authoritative definition of GAUC, nDCG@5 and primary. Reimplementing it — even
"equivalently" — is prohibited by CONTRIBUTING.md, because a divergent definition would
silently invalidate every comparison in the project.

What this module adds: input validation, useful error messages, and a stable import
path so callers never depend on sys.path manipulation.

Contract: C-04.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from src.paths import ensure_starter_kit_importable

ensure_starter_kit_importable()
from evaluate import evaluate as official_evaluate  # noqa: E402  (organizer reference)

#: Published FM seed std on primary. Used as the significance floor across the project.
SEED_STD_PRIMARY = 0.0008
#: Two sigma. A delta smaller than this is not a result.
SIGNIFICANCE_FLOOR = 2 * SEED_STD_PRIMARY  # 0.0016


class ScoreValidationError(ValueError):
    """Raised when scores cannot be evaluated (wrong length, NaN, Inf)."""


def validate_scores(
    user_ids: Sequence[Any], labels: Sequence[Any], scores: Sequence[float]
) -> None:
    """Check the three arrays satisfy contract C-04 before evaluating.

    The organizer evaluator would happily rank NaNs into an arbitrary position, so we
    reject non-finite scores here rather than producing a meaningless metric.
    """
    n = len(user_ids)
    if not (len(labels) == n == len(scores)):
        raise ScoreValidationError(
            f"length mismatch: user_ids={n}, labels={len(labels)}, scores={len(scores)}"
        )
    if n == 0:
        raise ScoreValidationError("empty evaluation input")
    for i, s in enumerate(scores):
        v = float(s)
        if math.isnan(v) or math.isinf(v):
            raise ScoreValidationError(f"non-finite score at row {i}: {s!r}")


def evaluate(
    user_ids: Sequence[Any],
    labels: Sequence[Any],
    scores: Sequence[float],
    k: int = 5,
) -> dict:
    """Validate, then delegate to the official evaluator.

    Returns {'GAUC', 'nDCG@5', 'primary', 'users', 'rows'} exactly as the organizer
    implementation does.
    """
    validate_scores(user_ids, labels, scores)
    return official_evaluate(user_ids, labels, scores, k=k)


def is_significant(delta_primary: float) -> bool:
    """True when a primary delta clears the 2-sigma seed-noise floor.

    A single-seed movement below this is noise. See docs/runbooks/EXPERIMENT_RUN.md.
    """
    return abs(delta_primary) > SIGNIFICANCE_FLOOR
