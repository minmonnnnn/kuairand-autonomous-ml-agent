"""Convergence and termination logic. Owner: Sarthak."""
from src.experiments.convergence import ConvergenceTracker, TerminalState


def test_running_while_improving():
    t = ConvergenceTracker()
    for p in [0.60, 0.61, 0.62, 0.63, 0.64]:
        t.record(p)
    assert t.state() == TerminalState.RUNNING


def test_converges_on_a_flat_plateau():
    t = ConvergenceTracker()
    for p in [0.60, 0.6005, 0.6008, 0.6009]:
        t.record(p)
    assert t.is_converged()
    assert t.state() == TerminalState.CONVERGED


def test_a_single_big_jump_prevents_convergence():
    t = ConvergenceTracker()
    for p in [0.60, 0.6005, 0.6300, 0.6301]:
        t.record(p)
    assert not t.is_converged()


def test_needs_more_than_n_iterations_before_it_can_converge():
    t = ConvergenceTracker(n=3)
    t.record(0.60)
    t.record(0.60)
    t.record(0.60)
    assert not t.is_converged()
    t.record(0.60)
    assert t.is_converged()


def test_boundary_exactly_at_epsilon_does_not_count_as_improvement():
    """Improvement must be strictly greater than epsilon."""
    t = ConvergenceTracker(epsilon=0.002, n=3)
    t.record(0.600)
    t.record(0.602)  # exactly epsilon
    t.record(0.604)
    t.record(0.606)
    assert t.is_converged()


def test_best_tracks_the_peak_not_the_last():
    t = ConvergenceTracker()
    for p in [0.60, 0.65, 0.61]:
        t.record(p)
    assert t.best == 0.65
    assert t.best_iteration == 1


def test_max_iterations_terminates():
    t = ConvergenceTracker(max_iterations=5)
    for i in range(5):
        t.record(0.60 + i * 0.05)  # still improving
    assert t.state() == TerminalState.MAX_ITERATIONS


def test_timeout_terminates_and_outranks_convergence():
    t = ConvergenceTracker(max_wall_clock_seconds=10)
    t.record(0.60, elapsed_seconds=11)
    assert t.state() == TerminalState.TIMEOUT
    assert t.should_stop()
