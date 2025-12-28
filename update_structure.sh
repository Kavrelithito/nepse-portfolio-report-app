#!/bin/bash

#
# Usage:
#   cd ~/MEGA/Nepse_portfoli/Nepse_portfolio_summary_pr
#   ./update_structure.sh
#
# Purpose:
#   Auto-generate PROJECT_STRUCTURE.txt from current filesystem
#

set -e

OUT="PROJECT_STRUCTURE.txt"

echo "Updating project structure..."

tree -a -L 4 \
  -I ".git|.venv|__pycache__|.pytest_cache|.mypy_cache|.ruff_cache|Untitled Folder" \
  > "$OUT"

echo "Done -> $OUT"


