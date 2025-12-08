"""
Unit tests for API headers and timeout behavior.
"""

from typing import Any

from deepsights._version import __version__
from deepsights.api.api import API


class _DummyResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def json(self):
        return {"ok": True}


def test_user_agent_header_uses_single_source_version(monkeypatch):
    api = API(endpoint_base="https://example.invalid/")
    ua = api._session.headers.get("User-Agent")
    assert ua == f"deepsights-api/{__version__}"


def test_default_timeout_env_override(monkeypatch):
    monkeypatch.setenv("DEEPSIGHTS_HTTP_TIMEOUT", "42")
    api = API(endpoint_base="https://example.invalid/")

    captured = {}

    def fake_get(url: str, params: Any = None, timeout: Any = None, headers: Any = None):
        captured["timeout"] = timeout
        return _DummyResponse(200)

    # Patch the session.get to avoid network and capture timeout
    api._session.get = fake_get  # type: ignore[method-assign]
    api.get("/ping")

    assert captured["timeout"] == 42
