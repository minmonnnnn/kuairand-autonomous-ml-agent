"""Canonical repository paths. Owner: Min. Status: IMPLEMENTED.

Every module resolves paths through here so that nothing depends on the caller's
working directory. Do not hardcode relative paths elsewhere.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STARTER_KIT = REPO_ROOT / "starter_kit"
CONFIGS = REPO_ROOT / "configs"
EXPERIMENTS = REPO_ROOT / "experiments"
RESEARCH = REPO_ROOT / "research"
RUNS = REPO_ROOT / "runs"
LOGS = REPO_ROOT / "logs"
ARTIFACTS = REPO_ROOT / "artifacts"

CHECKPOINTS = ARTIFACTS / "checkpoints"
METRICS = ARTIFACTS / "metrics"
SUBMISSIONS = ARTIFACTS / "submissions"
REPORTS = ARTIFACTS / "reports"

ITERATION_LOGS = LOGS / "iterations"
AGENT_LOGS = LOGS / "agent"
ERROR_LOGS = LOGS / "errors"
RESOURCE_LOGS = LOGS / "resources"


def data_dir() -> Path:
    """Resolve the KuaiRand-Pure data directory.

    Order: KUAIRAND_DATA_DIR env var, then ./KuaiRand-Pure/data at the repo root.
    """
    env = os.environ.get("KUAIRAND_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return REPO_ROOT / "KuaiRand-Pure" / "data"


def ensure_starter_kit_importable() -> None:
    """Put starter_kit/ on sys.path so its modules import by their own names.

    The organizer code uses flat imports (`from data import load`), so it has to be
    importable as a top-level package directory. We never modify those files.
    """
    import sys

    p = str(STARTER_KIT)
    if p not in sys.path:
        sys.path.insert(0, p)
