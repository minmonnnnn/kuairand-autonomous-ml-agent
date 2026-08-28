#!/usr/bin/env bash
# Validate a submission with the organizer checker.
#   scripts/submission/check_submission.sh artifacts/submissions/final.csv test
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_DIR="${KUAIRAND_DATA_DIR:-$REPO_ROOT/KuaiRand-Pure/data}"
FILE="${1:?usage: check_submission.sh <file> [valid|test]}"
SPLIT="${2:-valid}"

cd "$REPO_ROOT/starter_kit"
python3 submit.py --check --split "$SPLIT" --data_dir "$DATA_DIR" "$REPO_ROOT/$FILE"

echo "Reminder: test must have exactly 170,588 rows with strictly increasing row_id."
