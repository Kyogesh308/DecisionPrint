#!/usr/bin/env bash
set -euo pipefail
ALLOWED='^(intelligence/|eval/|scripts/p2/|tests/p2/|docs/p2_notes\.md$|requirements/p2\.txt$)'
bad=$(git diff --name-only main...HEAD | grep -Ev "$ALLOWED" || true)
if [ -n "$bad" ]; then echo "Files outside P2 ownership:"; echo "$bad"; exit 1; fi
ruff check intelligence eval scripts/p2 tests/p2
ruff format --check intelligence eval scripts/p2 tests/p2
pytest tests/p2 -q
python scripts/p2/run_demo_cache_check.py || true
echo "merge-ready"
