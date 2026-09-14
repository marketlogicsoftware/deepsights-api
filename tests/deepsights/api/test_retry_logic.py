# Copyright 2024-2025 Market Logic Software AG.

"""
Unit tests for retry decision logic and rate-limit conversion.
"""

from unittest.mock import Mock

import pytest
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tenacity import RetryCallState

from deepsights.api.api import (
    _handle_persistent_rate_limit,
    _retry_predicate,
    _should_retry_http_error,
)
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


def _retry_state(exception: Exception, **kwargs):
    """Build a tenacity retry state carrying the given failed outcome."""
    state = RetryCallState(retry_object=None, fn=None, args=(), kwargs=kwargs)
    state.set_exception((type(exception), exception, exception.__traceback__))
    return state


def test_retry_predicate_unwraps_the_retry_state():
    # tenacity hands the predicate a retry state, not the exception itself
    assert _retry_predicate(_retry_state(ConnectionError("conn"))) is True
    assert _retry_predicate(_retry_state(Timeout("timeout"))) is True

    r404 = Mock()
    r404.status_code = 404
    assert _retry_predicate(_retry_state(HTTPError("404 Not Found", response=r404))) is False


def test_retry_predicate_honors_retry_on_timeout_opt_out():
    # timeouts are not retried when the caller opted out ...
    assert _retry_predicate(_retry_state(Timeout("timeout"), retry_on_timeout=False)) is False

    # ... but connection errors and retriable status codes still are
    assert _retry_predicate(_retry_state(ConnectionError("conn"), retry_on_timeout=False)) is True

    r500 = Mock()
    r500.status_code = 500
    assert _retry_predicate(_retry_state(HTTPError("500 Server Error", response=r500), retry_on_timeout=False)) is True
