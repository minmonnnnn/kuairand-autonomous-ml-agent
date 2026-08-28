#!/usr/bin/env bash
# Reproduce the official FM baseline. See docs/runbooks/BASELINE_REPRODUCTION.md.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_DIR="${KUAIRAND_DATA_DIR:-$REPO_ROOT/KuaiRand-Pure/data}"
SEEDS="${SEEDS:-0}"

if [ ! -d "$DATA_DIR" ]; then
  echo "Dataset not found at $DATA_DIR" >&2
  echo "See docs/runbooks/LOCAL_SETUP.md" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/logs/iterations"
cd "$REPO_ROOT/starter_kit"

echo "== harness self-check: random must give test primary ~0.4753 =="
python3 baseline.py --model random --data_dir "$DATA_DIR"

echo
echo "== official FM baseline: expect valid primary ~0.6016, test ~0.5946 =="
for s in $SEEDS; do
  echo "--- seed $s ---"
  python3 baseline.py --model fm --seed "$s" --data_dir "$DATA_DIR" \
    | tee "$REPO_ROOT/logs/iterations/exp0000_seed${s}.log"
done

echo
echo "Now record EXP-0000-OFFICIAL-BASELINE per docs/runbooks/BASELINE_REPRODUCTION.md."
