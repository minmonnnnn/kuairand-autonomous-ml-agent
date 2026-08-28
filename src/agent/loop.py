"""Research loop skeleton. Owner: Min. Status: SCAFFOLDED.

This is the control flow only. Every component below is a protocol with no
implementation — no LLM is called, no experiment is run. It exists so the loop's shape
can be reviewed and tested with stubs before the pieces land. See task T-104.

Do not describe this as implemented.
"""
from __future__ import annotations

import time
from typing import Any, Protocol

from src.experiments.convergence import ConvergenceTracker, TerminalState
from src.monitoring.schema import ResourceUsage
from src.registry.registry import ExperimentRegistry


class Planner(Protocol):
    def next_spec(self, history: list, registry: ExperimentRegistry) -> Any: ...


class Runner(Protocol):
    def run(self, spec: Any) -> Any: ...


class Evaluator(Protocol):
    def summarize(self, run_result: Any, spec: Any) -> Any: ...


class Reflector(Protocol):
    def reflect(self, summary: Any, history: list) -> str: ...


class ResearchLoop:
    """hypothesis -> plan -> execute -> evaluate -> record -> reflect -> select."""

    def __init__(
        self,
        planner: Planner,
        runner: Runner,
        evaluator: Evaluator,
        reflector: Reflector,
        registry: ExperimentRegistry | None = None,
        tracker: ConvergenceTracker | None = None,
    ) -> None:
        self.planner = planner
        self.runner = runner
        self.evaluator = evaluator
        self.reflector = reflector
        self.registry = registry or ExperimentRegistry()
        self.tracker = tracker or ConvergenceTracker()
        self.resources = ResourceUsage()
        self.history: list = []

    def run(self) -> dict:
        """Iterate until a terminal state. Returns the run summary."""
        start = time.monotonic()

        while not self.tracker.should_stop():
            spec = self.planner.next_spec(self.history, self.registry)
            if spec is None:
                break

            run_result = self.runner.run(spec)
            summary = self.evaluator.summarize(run_result, spec)

            # Both accepted and rejected outcomes are recorded. Never delete a failure.
            self.history.append({"spec": spec, "result": run_result, "summary": summary})
            self.resources.iterations += 1

            primary = getattr(summary, "metrics", {}).get("primary")
            if primary is not None:
                self.tracker.record(primary, elapsed_seconds=time.monotonic() - start)

            self.reflector.reflect(summary, self.history)

        self.resources.agent_wall_clock_seconds = time.monotonic() - start
        return {
            "terminal_state": self.tracker.state(),
            "converged": self.tracker.state() == TerminalState.CONVERGED,
            "convergence": self.tracker.summary(),
            "resources": self.resources.to_json(),
            "validation_best": (
                self.registry.validation_best().experiment_id
                if self.registry.validation_best()
                else None
            ),
        }
