"""
Unit tests for API error mapping.
"""

from typing import Any, cast

import pytest
from requests import Response
from requests.exceptions import HTTPError

from deepsights.api.api import API, _handle_http_error
from deepsights.exceptions import AuthenticationError


class _Resp:
    def __init__(self, status):
        self.status_code = status

    def raise_for_status(self):
        raise HTTPError(f"{self.status_code}", response=cast(Response, self))

    def json(self):
        return {}


def test_handle_http_error_401_maps_to_authentication_error():
    with pytest.raises(AuthenticationError):
        _handle_http_error(cast(Response, _Resp(401)))


def test_handle_http_error_429_maps_to_http_error():
    with pytest.raises(HTTPError):
        _handle_http_error(cast(Response, _Resp(429)))


def test_api_get_404_passes_http_error(monkeypatch):
    api = API(endpoint_base="https://example.invalid/")

    def fake_get(url: str, params: Any = None, timeout: Any = None, headers: Any = None):
        return _Resp(404)

    api._session.get = fake_get  # type: ignore[method-assign]

    with pytest.raises(HTTPError):
        api.get("/not-found")
