"""Data loading adapter. Owner: Rishi. Status: IMPLEMENTED.

Wraps starter_kit/data.py rather than reimplementing it, because the submission row_id
is defined by that file's exact row ordering (contract C-01). Any independent loader
risks a silent misalignment that submit.py --check would catch only at the very end.

Adds: the split access guard, and row-count verification against the published numbers.
"""
from __future__ import annotations

from collections.abc import Iterable

from src.data.guard import FinalSubmissionToken, Split, check_access
from src.paths import data_dir as default_data_dir
from src.paths import ensure_starter_kit_importable

ensure_starter_kit_importable()
from data import FIELDS, LABEL, SPLITS, encode, load  # noqa: E402 (organizer reference)

#: Published row counts. A mismatch means the wrong dataset variant or a broken load.
EXPECTED_ROW_COUNTS = {"train": 1_141_112, "valid": 124_909, "test": 170_588}

__all__ = [
    "load_splits",
    "encode",
    "FIELDS",
    "LABEL",
    "SPLITS",
    "EXPECTED_ROW_COUNTS",
]


class RowCountMismatch(RuntimeError):
    """Loaded row counts do not match the published KuaiRand-Pure counts."""


def load_splits(
    data_dir=None,
    splits: Iterable[Split] = (Split.TRAIN, Split.VALID),
    token: FinalSubmissionToken | None = None,
    verify_counts: bool = True,
) -> dict:
    """Load the requested splits, enforcing the access policy.

    Args:
        data_dir: KuaiRand-Pure data directory. Defaults to KUAIRAND_DATA_DIR.
        splits: which splits to return. Test requires a FinalSubmissionToken.
        token: authorisation for FINAL-ONLY data.
        verify_counts: check loaded rows against EXPECTED_ROW_COUNTS.

    Returns:
        {split_name: list[row]} where row is the C-01 tuple
        (date, user_id, video_id, author_id, tab, duration_ms, label).
    """
    splits = tuple(Split(s) for s in splits)
    for s in splits:
        check_access(s, token)

    path = str(data_dir or default_data_dir())
    all_splits = load(path)

    if verify_counts:
        for name, expected in EXPECTED_ROW_COUNTS.items():
            got = len(all_splits.get(name, []))
            if got != expected:
                raise RowCountMismatch(
                    f"split '{name}': loaded {got:,} rows, expected {expected:,}. "
                    "Check that this is KuaiRand-Pure (not 1K or 27K) and that "
                    "starter_kit/data.py is unmodified."
                )

    return {s.value: all_splits[s.value] for s in splits}
