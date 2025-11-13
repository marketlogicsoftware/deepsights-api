#!/usr/bin/env bash
set -euo pipefail

echo "[precommit] Bootstrapping env with uv (.[test,lint])"
if command -v uv >/dev/null 2>&1; then
  uv pip install -q -e ".[test,lint]"
else
  echo "[precommit] uv not found. Install uv or run 'pip install -e .[lint]'" >&2
fi

# Load local env if present
if [ -f .env ]; then
  echo "[precommit] Loading .env into environment"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

echo "[precommit] Ruff lint (fix)"
uv run ruff check --fix .

echo "[precommit] Ruff format"
uv run ruff format .

echo "[precommit] mypy type-checks (src + tests)"
MYPYPATH="typings${MYPYPATH:+:$MYPYPATH}" uv run mypy --config-file mypy.ini deepsights tests

echo "[precommit] pytest core (fast test subset)"
uv run pytest -q -m "not heavy"

if command -v pre-commit >/dev/null 2>&1; then
  echo "[precommit] Validating hooks via pre-commit (all files)"
  pre-commit run --all-files
else
  echo "[precommit] pre-commit not installed; skipping hook validation" >&2
fi

echo "[precommit] Done"
