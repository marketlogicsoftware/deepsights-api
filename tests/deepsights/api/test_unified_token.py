# Copyright 2024-2025 Market Logic Software AG.

"""
Unit tests for UnifiedTokenMixin class.
"""

import threading
from typing import Any, cast
from unittest.mock import Mock

import pytest
from requests import Response
from requests.exceptions import HTTPError

from deepsights.api.api import API
from deepsights.api.unified_token import UnifiedTokenMixin
from deepsights.exceptions import AuthenticationError, TokenRefreshError


class _MockResponse:
    """Mock response object for testing."""

    def __init__(self, status_code: int, json_data: dict | None = None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.content = b"content"

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPError(f"{self.status_code}", response=cast(Response, self))

    def json(self) -> dict:
        return self._json_data


class MockUnifiedClient(UnifiedTokenMixin, API):
    """Mock client combining UnifiedTokenMixin with API for testing."""

    def __init__(
        self,
        unified_token: str,
        refresh_callback: Any,
        endpoint_base: str = "https://example.invalid/",
    ):
        API.__init__(self, endpoint_base=endpoint_base)
        self.__init_unified_token__(unified_token, refresh_callback)


class TestUnifiedTokenMixinInit:
    """Tests for UnifiedTokenMixin initialization."""

    def test_init_stores_token_and_mode(self):
        """Verify token is stored and unified mode is enabled on initialization."""
        callback = Mock(return_value="new_token")
        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=callback)

        assert client._unified_token == "initial_token"
        assert client._unified_token_mode is True
        # Token should NOT be on session headers (thread-safety)
        assert "Authorization" not in client._session.headers

    def test_get_auth_headers_returns_bearer_token(self):
        """Verify _get_auth_headers returns correct Authorization header."""
        callback = Mock(return_value="new_token")
        client = MockUnifiedClient(unified_token="test_token", refresh_callback=callback)

        headers = client._get_auth_headers()
        assert headers == {"Authorization": "Bearer test_token"}

    def test_unified_token_property(self):
        """Verify unified_token property returns current token."""
        callback = Mock(return_value="new_token")
        client = MockUnifiedClient(unified_token="test_token", refresh_callback=callback)

        assert client.unified_token == "test_token"


class TestUnifiedTokenRefresh:
    """Tests for token refresh functionality."""

    def test_refresh_callback_called_and_token_updated(self):
        """Verify refresh callback is invoked and internal token is updated."""
        callback = Mock(return_value="refreshed_token")
        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=callback)

        new_token = client._refresh_unified_token()

        callback.assert_called_once()
        assert new_token == "refreshed_token"
        assert client._unified_token == "refreshed_token"
        # Verify _get_auth_headers reflects the new token
        assert client._get_auth_headers() == {"Authorization": "Bearer refreshed_token"}

    def test_refresh_callback_empty_token_raises_error(self):
        """Verify TokenRefreshError is raised when callback returns empty."""
        callback = Mock(return_value="")
        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=callback)

        with pytest.raises(TokenRefreshError) as exc:
            client._refresh_unified_token()

        assert "empty token" in str(exc.value)

    def test_refresh_callback_none_signals_permanent_failure(self):
        """Verify None return signals permanent failure (returns None, doesn't raise)."""
        callback = Mock(return_value=None)
        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=callback)

        result = client._refresh_unified_token()

        assert result is None
        # Token should remain unchanged
        assert client._unified_token == "initial_token"

    def test_refresh_callback_exception_wrapped(self):
        """Verify callback exceptions are wrapped in TokenRefreshError."""
        callback = Mock(side_effect=RuntimeError("connection failed"))
        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=callback)

        with pytest.raises(TokenRefreshError) as exc:
            client._refresh_unified_token()

        assert "Token refresh failed" in str(exc.value)
        assert exc.value.__cause__ is not None


class TestExecuteWithRefresh:
    """Tests for _execute_with_refresh method."""

    def test_request_retried_after_successful_refresh(self):
        """Verify original request is retried with new token after 401."""
        call_count = 0

        def refresh_callback():
            return "new_token"

        def mock_request():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise AuthenticationError("401 Unauthorized")
            return {"result": "success"}

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)

        result = client._execute_with_refresh("GET /test", mock_request)

        assert result == {"result": "success"}
        assert call_count == 2
        assert client._unified_token == "new_token"

    def test_max_refresh_attempts_enforced(self):
        """Verify AuthenticationError after MAX_REFRESH_ATTEMPTS exhausted."""
        refresh_count = 0

        def refresh_callback():
            nonlocal refresh_count
            refresh_count += 1
            return f"token_v{refresh_count}"

        def mock_request():
            raise AuthenticationError("401 Unauthorized")

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)

        with pytest.raises(AuthenticationError) as exc:
            client._execute_with_refresh("GET /test", mock_request)

        assert "after 2 token refresh attempts" in str(exc.value)
        assert refresh_count == 2

    def test_refresh_failure_raises_authentication_error(self):
        """Verify AuthenticationError when refresh callback fails."""

        def refresh_callback():
            raise RuntimeError("refresh failed")

        def mock_request():
            raise AuthenticationError("401 Unauthorized")

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)

        with pytest.raises(AuthenticationError) as exc:
            client._execute_with_refresh("GET /test", mock_request)

        assert "Token refresh failed" in str(exc.value)

    def test_none_return_stops_retrying_immediately(self):
        """Verify that returning None from callback stops retrying immediately."""
        request_count = 0
        refresh_count = 0

        def refresh_callback():
            nonlocal refresh_count
            refresh_count += 1
            return None  # Signal permanent failure

        def mock_request():
            nonlocal request_count
            request_count += 1
            raise AuthenticationError("401 Unauthorized")

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)

        with pytest.raises(AuthenticationError) as exc:
            client._execute_with_refresh("GET /test", mock_request)

        assert "permanent auth failure" in str(exc.value)
        assert request_count == 1  # Only one request attempt
        assert refresh_count == 1  # Only one refresh attempt (then stopped)


class TestHTTPMethodOverrides:
    """Tests for overridden HTTP methods."""

    def test_get_with_401_triggers_refresh(self):
        """Verify GET request triggers refresh on 401."""
        call_count = 0
        captured_headers: list = []

        def refresh_callback():
            return "refreshed_token"

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)

        def mock_session_get(url, params=None, timeout=None, headers=None):
            nonlocal call_count
            call_count += 1
            captured_headers.append(headers)
            if call_count == 1:
                return _MockResponse(401)
            return _MockResponse(200, {"data": "value"})

        client._session.get = mock_session_get  # type: ignore[method-assign]

        result = client.get("/test")

        assert result == {"data": "value"}
        assert call_count == 2
        # First request uses initial token, second uses refreshed token
        assert captured_headers[0] == {"Authorization": "Bearer initial_token"}
        assert captured_headers[1] == {"Authorization": "Bearer refreshed_token"}

    def test_post_with_401_triggers_refresh(self):
        """Verify POST request triggers refresh on 401."""
        call_count = 0
        captured_headers: list = []

        def refresh_callback():
            return "refreshed_token"

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)

        def mock_session_post(url, params=None, json=None, timeout=None, headers=None):
            nonlocal call_count
            call_count += 1
            captured_headers.append(headers)
            if call_count == 1:
                return _MockResponse(401)
            return _MockResponse(200, {"created": True})

        client._session.post = mock_session_post  # type: ignore[method-assign]

        result = client.post("/test", body={"key": "value"})

        assert result == {"created": True}
        assert call_count == 2
        # First request uses initial token, second uses refreshed token
        assert captured_headers[0] == {"Authorization": "Bearer initial_token"}
        assert captured_headers[1] == {"Authorization": "Bearer refreshed_token"}

    def test_successful_request_no_refresh(self):
        """Verify successful request does not trigger refresh."""
        refresh_callback = Mock(return_value="new_token")
        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)
        captured_headers: list = []

        def mock_session_get(url, params=None, timeout=None, headers=None):
            captured_headers.append(headers)
            return _MockResponse(200, {"data": "value"})

        client._session.get = mock_session_get  # type: ignore[method-assign]

        result = client.get("/test")

        assert result == {"data": "value"}
        refresh_callback.assert_not_called()
        # Verify headers were passed per-request
        assert captured_headers[0] == {"Authorization": "Bearer initial_token"}


class TestUnifiedTokenModeBypass:
    """Tests for bypassing mixin when not in unified token mode."""

    def test_bypass_when_not_unified_mode(self):
        """Verify mixin delegates to super() when _unified_token_mode=False."""

        class DirectAPI(UnifiedTokenMixin, API):
            def __init__(self):
                API.__init__(self, endpoint_base="https://example.invalid/")
                # Do NOT call __init_unified_token__, so _unified_token_mode is False

        client = DirectAPI()

        # _unified_token_mode should not be set or should be False
        assert getattr(client, "_unified_token_mode", False) is False

        # Calling get should not trigger any mixin refresh logic
        def mock_session_get(url, params=None, timeout=None, headers=None):
            return _MockResponse(200, {"data": "value"})

        client._session.get = mock_session_get  # type: ignore[method-assign]

        result = client.get("/test")
        assert result == {"data": "value"}


class TestThreadSafety:
    """Basic thread safety tests for token refresh."""

    def test_get_auth_headers_uses_lock(self):
        """Verify _get_auth_headers acquires lock for thread-safe reads."""
        lock_acquired_count = 0
        original_lock_class = threading.Lock

        class CountingLock:
            def __init__(self):
                self._lock = original_lock_class()

            def __enter__(self):
                nonlocal lock_acquired_count
                self._lock.__enter__()
                lock_acquired_count += 1
                return self

            def __exit__(self, *args):
                return self._lock.__exit__(*args)

        callback = Mock(return_value="new_token")
        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=callback)
        client._unified_token_lock = CountingLock()  # type: ignore[assignment]

        # Reading headers should acquire the lock
        headers = client._get_auth_headers()

        assert lock_acquired_count == 1
        assert headers == {"Authorization": "Bearer initial_token"}

    def test_concurrent_refresh_uses_lock(self):
        """Verify lock is used during concurrent refresh attempts."""
        refresh_count = 0
        lock_acquired_count = 0

        original_lock_class = threading.Lock

        class CountingLock:
            def __init__(self):
                self._lock = original_lock_class()

            def __enter__(self):
                nonlocal lock_acquired_count
                self._lock.__enter__()
                lock_acquired_count += 1
                return self

            def __exit__(self, *args):
                return self._lock.__exit__(*args)

        def refresh_callback():
            nonlocal refresh_count
            refresh_count += 1
            return f"token_v{refresh_count}"

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)
        client._unified_token_lock = CountingLock()  # type: ignore[assignment]

        # Perform multiple refreshes
        client._refresh_unified_token()
        client._refresh_unified_token()

        assert lock_acquired_count == 2
        assert refresh_count == 2

    def test_skip_refresh_if_token_already_updated(self):
        """Verify redundant refresh is skipped if another thread already refreshed."""
        refresh_count = 0

        def refresh_callback():
            nonlocal refresh_count
            refresh_count += 1
            return f"token_v{refresh_count}"

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=refresh_callback)

        # First refresh succeeds
        client._refresh_unified_token(failed_token="initial_token")
        assert refresh_count == 1
        assert client._unified_token == "token_v1"

        # Second refresh with same failed_token should be skipped
        # (simulates another thread that was waiting on the lock)
        client._refresh_unified_token(failed_token="initial_token")
        assert refresh_count == 1  # Still 1, callback not called again
        assert client._unified_token == "token_v1"

    def test_refresh_proceeds_if_token_matches_failed(self):
        """Verify refresh proceeds when current token matches the failed token."""
        refresh_count = 0

        def refresh_callback():
            nonlocal refresh_count
            refresh_count += 1
            return f"token_v{refresh_count}"

        client = MockUnifiedClient(unified_token="stale_token", refresh_callback=refresh_callback)

        # Refresh should proceed since current token matches failed token
        client._refresh_unified_token(failed_token="stale_token")
        assert refresh_count == 1
        assert client._unified_token == "token_v1"

    def test_concurrent_401_only_one_refresh(self):
        """Simulate concurrent 401s - only one thread should refresh."""
        import time

        refresh_count = 0
        refresh_started = threading.Event()
        refresh_can_complete = threading.Event()

        def slow_refresh_callback():
            nonlocal refresh_count
            refresh_started.set()
            refresh_can_complete.wait(timeout=5)
            refresh_count += 1
            return f"token_v{refresh_count}"

        client = MockUnifiedClient(unified_token="initial_token", refresh_callback=slow_refresh_callback)

        results = []
        errors = []

        def thread_refresh(failed_token: str):
            try:
                result = client._refresh_unified_token(failed_token=failed_token)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start first thread - it will start refresh and wait
        t1 = threading.Thread(target=thread_refresh, args=("initial_token",))
        t1.start()

        # Wait for first thread to start refresh
        refresh_started.wait(timeout=5)

        # Start second thread with same failed token - should skip refresh
        t2 = threading.Thread(target=thread_refresh, args=("initial_token",))
        t2.start()

        # Allow refresh to complete
        time.sleep(0.1)  # Give t2 time to start waiting on lock
        refresh_can_complete.set()

        t1.join(timeout=5)
        t2.join(timeout=5)

        assert len(errors) == 0
        assert refresh_count == 1  # Only one actual refresh
        assert len(results) == 2  # Both threads got a result
        assert all(r == "token_v1" for r in results)  # Both got same token
