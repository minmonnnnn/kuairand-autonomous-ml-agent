"""Model framework. Owner: Vidush. Status: SCAFFOLDED. Contract: C-03.

NOT YET IMPLEMENTED: no concrete model exists. Task T-301 is the FM parity gate — our
FM must reach valid primary within 0.002 of the organizer's 0.6016 before anything
downstream can be trusted.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np


class TrainingDiverged(RuntimeError):
    """NaN or Inf appeared during training. Save nothing; let recovery decide."""


@dataclass
class TrainingResult:
    """Outcome of one training run. Contract C-03."""

    checkpoint_path: str
    best_epoch: int
    epochs_run: int
    seed: int
    wall_clock_seconds: float
    early_stopped: bool = False
    train_metrics: list[dict] = field(default_factory=list)
    valid_metrics: list[dict] = field(default_factory=list)


class RankingModel(ABC):
    """Base class for every scorer.

    Selection rule, non-negotiable: early stopping and checkpoint selection use
    validation primary only. A test metric must never appear in a selection path.
    """

    name: str = "base"

    @abstractmethod
    def fit(self, train, valid, config: dict, seed: int = 0) -> TrainingResult:
        """Train, checkpointing the best-validation state (not the last state)."""

    @abstractmethod
    def predict(self, features) -> np.ndarray:
        """Score rows. Any real scale; only relative order within a user matters."""

    @abstractmethod
    def save(self, path: str) -> None: ...

    @abstractmethod
    def load(self, path: str) -> RankingModel: ...

    def describe(self) -> dict:
        return {"model": self.name}


_REGISTRY: dict[str, type[RankingModel]] = {}


def register(name: str):
    def deco(cls: type[RankingModel]) -> type[RankingModel]:
        if name in _REGISTRY:
            raise ValueError(f"model {name!r} already registered")
        _REGISTRY[name] = cls
        return cls

    return deco


def get_model(name: str) -> type[RankingModel]:
    if name not in _REGISTRY:
        raise KeyError(f"unknown model {name!r}; known: {sorted(_REGISTRY)}")
    return _REGISTRY[name]
