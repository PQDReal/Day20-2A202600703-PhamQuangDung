#!/usr/bin/env bash
set -euo pipefail
if grep -R "TODO(student)" -n src tests docs; then
  echo "Found unfinished lab TODO markers."
  exit 1
fi
echo "No unfinished lab TODO markers found."
