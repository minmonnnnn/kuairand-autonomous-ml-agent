"""The adapter must be numerically identical to the organizer evaluator. Owner: Sarthak."""
import random

import pytest

from src.evaluation.official import (
    SIGNIFICANCE_FLOOR,
    ScoreValidationError,
    evaluate,
    is_significant,
    official_evaluate,
)


def _synthetic(n=2000, seed=0):
    rng = random.Random(seed)
    users = [f"u{rng.randrange(120)}" for _ in range(n)]
    labels = [rng.randrange(2) for _ in range(n)]
    scores = [rng.random() for _ in range(n)]
    return users, labels, scores


def test_adapter_matches_official_exactly():
    u, y, s = _synthetic()
    assert evaluate(u, y, s) == official_evaluate(u, y, s)


def test_primary_is_the_mean_of_the_two_metrics():
    u, y, s = _synthetic()
    r = evaluate(u, y, s)
    assert r["primary"] == pytest.approx((r["GAUC"] + r["nDCG@5"]) / 2)


def test_perfect_scores_beat_random():
    u, y, _ = _synthetic()
    perfect = evaluate(u, y, [float(v) for v in y])
    rnd = evaluate(u, y, [random.Random(1).random() for _ in y])
    assert perfect["primary"] > rnd["primary"]


def test_rejects_nan_and_inf():
    u, y, s = _synthetic(n=50)
    for bad in (float("nan"), float("inf"), float("-inf")):
        s2 = list(s)
        s2[7] = bad
        with pytest.raises(ScoreValidationError):
            evaluate(u, y, s2)


def test_rejects_length_mismatch():
    u, y, s = _synthetic(n=50)
    with pytest.raises(ScoreValidationError):
        evaluate(u, y, s[:-1])


def test_significance_floor_is_two_sigma():
    assert SIGNIFICANCE_FLOOR == pytest.approx(0.0016)
    assert not is_significant(0.0010)   # noise
    assert is_significant(0.0030)       # a real movement
