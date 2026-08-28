"""FeatureBundle invariants (contract C-02). Owner: Rishi."""
import numpy as np
import pytest

from src.features.base import FeatureBuildError, FeatureBundle


def _bundle(**over):
    kw = dict(
        X=np.zeros((10, 3), dtype=np.int32),
        y=np.zeros(10, dtype=np.float32),
        users=[f"u{i}" for i in range(10)],
        field_dims=[4, 5, 6],
        total_dim=15,
        feature_version="fv-000",
    )
    kw.update(over)
    return FeatureBundle(**kw)


def test_valid_bundle_constructs():
    assert _bundle().total_dim == 15


def test_length_mismatch_is_rejected():
    with pytest.raises(FeatureBuildError):
        _bundle(users=["u0"])


def test_negative_ids_are_rejected():
    X = np.zeros((10, 3), dtype=np.int32)
    X[0, 0] = -1
    with pytest.raises(FeatureBuildError):
        _bundle(X=X)


def test_total_dim_must_match_field_dims():
    with pytest.raises(FeatureBuildError):
        _bundle(total_dim=99)


def test_dense_length_must_match():
    with pytest.raises(FeatureBuildError):
        _bundle(dense=np.zeros((3, 2), dtype=np.float32))
