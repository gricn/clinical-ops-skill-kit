#!/usr/bin/env bash
# Point git at the repo's `.githooks/` directory so the precommit gate runs.
# Run once after a fresh clone (or if the local config is wiped).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

git config core.hooksPath .githooks
echo "Configured core.hooksPath=.githooks"
