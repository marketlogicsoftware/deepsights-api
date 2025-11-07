# Copyright 2024-2025 Market Logic Software AG.

"""
Unit tests for retry decision logic and rate-limit conversion.
"""

from unittest.mock import Mock

import pytest
from requests.exceptions import ConnectionError, HTTPError, Timeout

from deepsights.api.api import _handle_persistent_rate_limit, _should_retry_http_error
from deepsights.exceptions import RateLimitError


def test_should_retry_http_error_status_codes():
    # 500 should retry
    r500 = Mock()
    r500.status_code = 500
    err500 = HTTPError("500 Server Error", response=r500)
    assert _should_retry_http_error(err500) is True

    # 429 should retry
    r429 = Mock()
    r429.status_code = 429
    err429 = HTTPError("429 Too Many Requests", response=r429)
    assert _should_retry_http_error(err429) is True

    # 404 should not retry
    r404 = Mock()
    r404.status_code = 404
    err404 = HTTPError("404 Not Found", response=r404)
    assert _should_retry_http_error(err404) is False


def test_should_retry_connection_and_timeout_errors():
    assert _should_retry_http_error(ConnectionError("conn")) is True
    assert _should_retry_http_error(Timeout("timeout")) is True


def test_persistent_429_converted_to_rate_limit_error():
    # Create a mock function that raises HTTPError with 429
    def mock_func():
        mock_response = Mock()
        mock_response.status_code = 429
        raise HTTPError("429 Too Many Requests", response=mock_response)

    decorated = _handle_persistent_rate_limit(mock_func)

    with pytest.raises(RateLimitError) as exc:
        decorated()

    assert "Server rate limit exceeded" in str(exc.value)
    assert exc.value.retry_after is None
