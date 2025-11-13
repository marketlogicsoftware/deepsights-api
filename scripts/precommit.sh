#!/usr/bin/env bash
set -euo pipefail

echo "[precommit] Bootstrapping lint env with uv (.[lint])"
if command -v uv >/dev/null 2>&1; then
  uv pip install -q -e ".[lint]"
else
  echo "[precommit] uv not found. Install uv or run 'pip install -e .[lint]'" >&2
fi

echo "[precommit] Ruff lint (fix)"
ruff check --fix .

echo "[precommit] Ruff format"
ruff format .

echo "[precommit] mypy type-checks"
MYPYPATH="typings${MYPYPATH:+:$MYPYPATH}" mypy --config-file mypy.ini deepsights

if command -v pre-commit >/dev/null 2>&1; then
  echo "[precommit] Validating hooks via pre-commit (all files)"
  pre-commit run --all-files
else
  echo "[precommit] pre-commit not installed; skipping hook validation" >&2
fi

echo "[precommit] Done"
