import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "starter_kit"))


def _data_dir() -> Path:
    env = os.environ.get("KUAIRAND_DATA_DIR")
    return Path(env) if env else REPO_ROOT / "KuaiRand-Pure" / "data"


@pytest.fixture(scope="session")
def data_dir() -> Path:
    d = _data_dir()
    if not d.exists():
        pytest.skip(f"dataset not found at {d}; see docs/runbooks/LOCAL_SETUP.md")
    return d
