"""Convergence and termination tracking. Owner: Sarthak. Status: IMPLEMENTED.

Three independent termination conditions, all of which must be tracked:

    CONVERGED       validation primary has not improved by more than epsilon
                    over the previous N consecutive iterations
    MAX_ITERATIONS  50 iterations reached
    TIMEOUT         6 hours of wall clock reached

epsilon = 0.002 is not arbitrary: FM's seed std on primary is 0.0008, so the threshold
sits at ~2.5 sigma. Movements below it cannot be distinguished from noise.
"""
from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_EPSILON = 0.002
DEFAULT_N = 3
DEFAULT_MAX_ITERATIONS = 50
DEFAULT_MAX_WALL_CLOCK_SECONDS = 6 * 60 * 60

#: Guards the epsilon comparison against binary float error (0.602-0.600 > 0.002).
_FLOAT_TOL = 1e-9


class TerminalState:
    RUNNING = "RUNNING"
    CONVERGED = "CONVERGED"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    TIMEOUT = "TIMEOUT"


@dataclass
class ConvergenceTracker:
    """Feed it one validation primary per iteration; ask it whether to stop."""

    epsilon: float = DEFAULT_EPSILON
    n: int = DEFAULT_N
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    max_wall_clock_seconds: float = DEFAULT_MAX_WALL_CLOCK_SECONDS

    history: list[float] = field(default_factory=list)
    best: float | None = None
    best_iteration: int | None = None
    elapsed_seconds: float = 0.0

    @property
    def iterations(self) -> int:
        return len(self.history)

    def record(self, validation_primary: float, elapsed_seconds: float | None = None) -> None:
        self.history.append(float(validation_primary))
        if elapsed_seconds is not None:
            self.elapsed_seconds = float(elapsed_seconds)
        if self.best is None or validation_primary > self.best:
            self.best = float(validation_primary)
            self.best_iteration = len(self.history) - 1

    def is_converged(self) -> bool:
        """True when none of the last N iterations improved the running best by > epsilon.

        'Improvement' is measured against the best seen *before* that iteration, so a
        run that plateaus after an early peak converges rather than drifting on.
        """
        if len(self.history) < self.n + 1:
            return False
        for i in range(len(self.history) - self.n, len(self.history)):
            prior_best = max(self.history[:i])
            # Strictly greater, with a tolerance: a delta of exactly epsilon is not an
            # improvement, and binary float error must not decide a convergence call.
            if (self.history[i] - prior_best) - self.epsilon > _FLOAT_TOL:
                return False
        return True

    def state(self) -> str:
        if self.elapsed_seconds >= self.max_wall_clock_seconds:
            return TerminalState.TIMEOUT
        if self.iterations >= self.max_iterations:
            return TerminalState.MAX_ITERATIONS
        if self.is_converged():
            return TerminalState.CONVERGED
        return TerminalState.RUNNING

    def should_stop(self) -> bool:
        return self.state() != TerminalState.RUNNING

    def summary(self) -> dict:
        return {
            "state": self.state(),
            "iterations": self.iterations,
            "best_primary": self.best,
            "best_iteration": self.best_iteration,
            "elapsed_seconds": self.elapsed_seconds,
            "epsilon": self.epsilon,
            "n": self.n,
        }
