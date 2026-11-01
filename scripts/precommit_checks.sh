#!/usr/bin/env bash
# Pre-commit gate for the skill kit.
# Order:
#   1. Skill registry consistency (SKILL.md ↔ AGENTS.md ↔ catalog).
#   2. Repo doc sync (new skill / workspace forces docs update in same commit).
#   3. Python syntax check on governance scripts.
# Wired in via `.githooks/pre-commit` after `./scripts/install_githooks.sh`.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV_PYTHON="$REPO_ROOT/.venv/bin/python"
if [[ -x "$VENV_PYTHON" ]]; then
  PYTHON="$VENV_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON="$(command -v python)"
else
  echo "ERROR: no usable Python interpreter found." >&2
  exit 1
fi

echo "[1/3] Skill registry"
"$PYTHON" scripts/check_skill_registry.py

echo "[2/3] Repo doc sync"
"$PYTHON" scripts/check_repo_docs_sync.py

echo "[3/3] Syntax checks"
"$PYTHON" -m py_compile \
  scripts/check_repo_docs_sync.py \
  scripts/check_skill_registry.py

"$PYTHON" scripts/check_public_privacy.py
"$PYTHON" -m unittest discover -s tests -p "test_*.py"
echo "All pre-commit checks passed."
