"""Data-dependent checks. Owner: Sarthak. Skipped unless the dataset is present."""
import pytest

from src.data.loader import EXPECTED_ROW_COUNTS, load_splits
from src.evaluation.official import evaluate

pytestmark = pytest.mark.requires_data


def test_split_row_counts(data_dir):
    from src.data.guard import Split

    s = load_splits(data_dir, splits=(Split.TRAIN, Split.VALID))
    assert len(s["train"]) == EXPECTED_ROW_COUNTS["train"]
    assert len(s["valid"]) == EXPECTED_ROW_COUNTS["valid"]


@pytest.mark.slow
def test_random_scoring_anchor(data_dir):
    """The organizers' prescribed harness self-check: random gives primary ~0.483 on valid."""
    import numpy as np

    from src.data.guard import Split

    s = load_splits(data_dir, splits=(Split.VALID,))
    rows = s["valid"]
    rng = np.random.default_rng(0)
    r = evaluate([x[1] for x in rows], [x[6] for x in rows], rng.random(len(rows)))
    assert r["primary"] == pytest.approx(0.4834, abs=0.003)
