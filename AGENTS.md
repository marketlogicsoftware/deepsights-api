# Repository Guidelines

## Project Structure & Module Organization
- `deepsights/` – library code: `deepsights/deepsights.py` (entry client), `documentstore/`, `contentstore/`, `userclient/`, `api/`, `utils/` (Pydantic models, helpers).
- `tests/` – pytest suite organized by feature (`contentstore/`, `documentstore/`, `userclient/`), plus shared `conftest.py` and `tests/data/`.
- `docs/` – generated API docs (built via pdoc, published by CI).
- `main.py` – runnable examples and quick demos.

## Build, Test, and Development Commands
- Create env: `python -m venv .venv && source .venv/bin/activate`
- Install dev deps (preferred): `pip install uv && uv pip install -e ".[test,lint,docs]"`
  - Pip alternative: `pip install -e ".[test,lint,docs]"`
- Run tests: `pytest` (requires API env vars; see Security section).
- Lint: `ruff check . && ruff format --check .`
- Build docs: `pdoc -o docs/ deepsights`
- Example run: `python main.py`

## Coding Style & Naming Conventions
- Python 3.10–3.12, 4‑space indentation, max line length 100.
- Naming: `snake_case` for functions/variables/modules; `PascalCase` for classes; `UPPER_CASE` for constants.
- Keep functions focused (≤5 args when possible). Favor type hints and Pydantic models.
- Lint with Ruff (see `pyproject.toml` for config). Fix issues or ignore with justification.

## Testing Guidelines
- Framework: pytest. Tests live under `tests/**/test_*.py`.
- Use shared fixtures in `tests/conftest.py` (e.g., `ds_client`, `user_client`, `test_data`).
- Run locally with required env configured; prefer mocking for network-heavy tests.
- Add tests with clear, descriptive names and assertions focused on public APIs.

## Commit & Pull Request Guidelines
- Commit messages: concise, imperative (“Add hybrid search”), optionally include scope. Tag versions as `vX.Y.Z` when releasing.
- PRs must: describe changes, note breaking changes, link issues, include tests, and update docs/examples when applicable.
- CI runs `pytest`, `ruff`, and docs build. Keep CI green.

## Security & Configuration Tips
- Do not commit credentials. Configure via env:
  - `DEEPSIGHTS_API_KEY` (required), `CONTENTSTORE_API_KEY` (optional), `MIP_API_KEY` (optional), `MIP_IDENTITY_VALID_EMAIL` (tests).
  - Example: `export DEEPSIGHTS_API_KEY=...`
- Respect API rate limits in tests and examples; use provided retry helpers.
