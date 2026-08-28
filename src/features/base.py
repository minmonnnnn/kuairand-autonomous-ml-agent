"""Feature framework. Owner: Rishi. Status: SCAFFOLDED. Contract: C-02.

This file defines the seam between Rishi and Vidush. Vidush codes against FeatureBundle
and never imports a concrete builder; Rishi can rewrite every builder without touching
model code.

NOT YET IMPLEMENTED: no concrete builder exists. See task T-203.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np


class FeatureBuildError(RuntimeError):
    """A feature could not be built. Always name the offending field."""


@dataclass
class FeatureBundle:
    """Model-ready features for one split. Row order must match contract C-01."""

    X: np.ndarray                      # int32 (N, F), offset-encoded categorical ids
    y: np.ndarray                      # float32 (N,), the long_view label
    users: list[str]                   # length N, user_id per row
    field_dims: list[int]              # per-field vocab size, including one UNK slot
    total_dim: int                     # sum(field_dims)
    feature_version: str
    dense: np.ndarray | None = None    # float32 (N, D) or None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        n = len(self.X)
        if not (len(self.y) == n == len(self.users)):
            raise FeatureBuildError(
                f"length mismatch: X={n}, y={len(self.y)}, users={len(self.users)}"
            )
        if self.dense is not None and len(self.dense) != n:
            raise FeatureBuildError(f"dense has {len(self.dense)} rows, expected {n}")
        if self.X.size and self.X.min() < 0:
            raise FeatureBuildError("negative feature id — offset encoding is wrong")
        if sum(self.field_dims) != self.total_dim:
            raise FeatureBuildError("total_dim does not match sum(field_dims)")


class FeatureBuilder(ABC):
    """Base class for every feature set.

    Hard rule: vocabularies and any statistic (quantile edges, popularity counts,
    behavioural aggregates) are fit on TRAIN ONLY. Fitting on valid is leakage and
    invalidates every downstream comparison.
    """

    #: Immutable version string, e.g. "fv-003". Once used in a recorded experiment it
    #: must never be reused for different logic.
    version: str = "fv-000"

    @abstractmethod
    def fit(self, train_rows: list) -> FeatureBuilder:
        """Learn vocabularies and statistics from train rows only."""

    @abstractmethod
    def transform(self, rows: list) -> FeatureBundle:
        """Encode rows into a FeatureBundle, preserving input row order."""

    def fit_transform(self, splits: dict) -> dict[str, FeatureBundle]:
        self.fit(splits["train"])
        return {name: self.transform(rows) for name, rows in splits.items()}

    def describe(self) -> dict:
        """Metadata for the experiment record. Override to add field-level detail."""
        return {"builder": type(self).__name__, "feature_version": self.version}


_REGISTRY: dict[str, type[FeatureBuilder]] = {}


def register(name: str):
    """Decorator registering a builder so configs can name it as a string."""

    def deco(cls: type[FeatureBuilder]) -> type[FeatureBuilder]:
        if name in _REGISTRY:
            raise ValueError(f"feature builder {name!r} already registered")
        _REGISTRY[name] = cls
        return cls

    return deco


def get_builder(name: str) -> type[FeatureBuilder]:
    if name not in _REGISTRY:
        raise KeyError(f"unknown feature builder {name!r}; known: {sorted(_REGISTRY)}")
    return _REGISTRY[name]
