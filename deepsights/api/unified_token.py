# Copyright 2024-2025 Market Logic Software AG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the UnifiedTokenMixin for unified token authentication.
"""

import logging
import threading
from typing import Any, Callable, Dict, List, Optional

from deepsights.exceptions import AuthenticationError, TokenRefreshError

logger = logging.getLogger(__name__)


class UnifiedTokenMixin:
    """
    Mixin providing unified token authentication with automatic 401 refresh.

    This mixin must be used with a class that inherits from API (or a subclass).
    It intercepts 401 Unauthorized responses and automatically refreshes the token
    using the provided callback, retrying the request up to MAX_REFRESH_ATTEMPTS times.

    Thread Safety:
        This mixin is designed for multi-threaded use with a shared client instance.
        When multiple threads receive 401 errors simultaneously, only one will
        perform the actual token refresh while others wait and reuse the result.

        Note: The underlying `requests.Session` is not fully thread-safe. For
        high-concurrency scenarios, consider using one client instance per thread.

    Important Behaviors:
        - If `expected_statuscodes` includes 401, the refresh logic will NOT trigger
          (the caller is assumed to be handling 401 responses explicitly).
        - The refresh callback should implement its own timeout to avoid blocking
          indefinitely, which would also block other threads waiting to refresh.

    Usage:
        class MyClient(UnifiedTokenMixin, APIKeyAPI):
            def __init__(self, unified_token, refresh_callback, ...):
                API.__init__(self, endpoint_base)
                self.__init_unified_token__(unified_token, refresh_callback)
    """

    MAX_REFRESH_ATTEMPTS: int = 2

    # Type hints for attributes (set by __init_unified_token__)
    _unified_token: str
    _refresh_callback: Callable[[], Optional[str]]
    _unified_token_lock: threading.Lock
    _unified_token_mode: bool

    def __init_unified_token__(
        self,
        unified_token: str,
        refresh_callback: Callable[[], Optional[str]],
    ) -> None:
        """
        Initialize unified token authentication.

        This method should be called by the subclass __init__ after
        initializing the base API class.

        Args:
            unified_token: The initial bearer token string.
            refresh_callback: A callable that returns a new token string, or None
                to signal permanent authentication failure (no further retries).
                The callback should handle obtaining a fresh token (e.g., by
                exchanging a refresh token). It takes no arguments.

                Return values:
                    - str: New valid token - will be used for retry
                    - None: Permanent failure - immediately raises AuthenticationError
                    - "" (empty): Treated as error, but may retry if attempts remain

                **Important:** The callback MUST implement its own timeout.
                A hung callback will hold the refresh lock and block all other
                threads attempting to refresh. Example with timeout::

                    def my_refresh_callback():
                        try:
                            response = requests.post(
                                "https://auth.example.com/token",
                                data={"refresh_token": my_refresh_token},
                                timeout=10  # Always set a timeout!
                            )
                            return response.json()["access_token"]
                        except Exception:
                            return None  # Signal permanent failure
        """
        self._unified_token = unified_token
        self._refresh_callback = refresh_callback
        self._unified_token_lock = threading.Lock()
        self._unified_token_mode = True

        # Note: We intentionally do NOT set Authorization on session.headers
        # because session.headers.update() is not thread-safe when called
        # concurrently. Instead, we pass the Authorization header per-request
        # in the overridden HTTP methods. This ensures thread-safety since
        # each request reads the current token under the lock.

        logger.debug("Unified token authentication initialized")

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get the Authorization header with the current token (thread-safe).

        This method reads the current token under the lock to ensure thread-safety.
        The returned headers dict can be passed to HTTP methods for per-request auth.

        Returns:
            Dict containing the Authorization header with Bearer token.
        """
        with self._unified_token_lock:
            return {"Authorization": f"Bearer {self._unified_token}"}

    def _refresh_unified_token(self, failed_token: Optional[str] = None) -> Optional[str]:
        """
        Thread-safe token refresh using the callback.

        Args:
            failed_token: The token that caused the 401. If provided and the current
                token is different, skip refresh (another thread already refreshed).

        Returns:
            The new token string (or current token if already refreshed).
            Returns None if the callback returned None (signals permanent failure).

        Raises:
            TokenRefreshError: If the callback raises an exception or returns empty string.
        """
        with self._unified_token_lock:
            # Check if another thread already refreshed the token
            if failed_token is not None and self._unified_token != failed_token:
                logger.debug("Token already refreshed by another thread, skipping")
                return self._unified_token

            logger.debug("Refreshing unified token via callback")
            try:
                new_token = self._refresh_callback()

                # None signals permanent failure - don't retry
                if new_token is None:
                    logger.warning("Refresh callback returned None, signaling permanent failure")
                    return None

                # Empty string is an error
                if not new_token:
                    raise TokenRefreshError("Refresh callback returned empty token")

                self._unified_token = new_token
                # Note: We do NOT update session.headers here because it's not
                # thread-safe. The token is read per-request in the HTTP methods.
                logger.info("Successfully refreshed unified token")
                return new_token

            except TokenRefreshError:
                raise
            except Exception as e:
                logger.error("Token refresh failed: %s", str(e))
                raise TokenRefreshError(f"Token refresh failed: {e}") from e

    def _execute_with_refresh(
        self,
        method_name: str,
        execute_fn: Callable[[], Any],
    ) -> Any:
        """
        Execute an HTTP method with automatic 401 refresh retry.

        Args:
            method_name: Name of the HTTP method (for logging).
            execute_fn: A callable that performs the HTTP request.

        Returns:
            The response from execute_fn.

        Raises:
            AuthenticationError: After MAX_REFRESH_ATTEMPTS exhausted or if refresh fails.
        """
        refresh_attempts = 0

        while True:
            # Capture the token used for this request attempt
            token_before_request = self._unified_token

            try:
                return execute_fn()

            except AuthenticationError:
                refresh_attempts += 1

                if refresh_attempts > self.MAX_REFRESH_ATTEMPTS:
                    logger.error(
                        "Max refresh attempts (%d) exhausted for %s",
                        self.MAX_REFRESH_ATTEMPTS,
                        method_name,
                    )
                    raise AuthenticationError(f"Authentication failed after {self.MAX_REFRESH_ATTEMPTS} token refresh attempts")

                logger.info(
                    "401 received for %s, attempting refresh (%d/%d)",
                    method_name,
                    refresh_attempts,
                    self.MAX_REFRESH_ATTEMPTS,
                )

                try:
                    # Pass the failed token so we can skip if another thread refreshed
                    new_token = self._refresh_unified_token(failed_token=token_before_request)

                    # None signals permanent failure - don't retry
                    if new_token is None:
                        raise AuthenticationError("Token refresh callback returned None, indicating permanent auth failure")
                except TokenRefreshError as e:
                    # Convert to AuthenticationError for consistent API
                    raise AuthenticationError(f"Token refresh failed; cannot authenticate: {e}") from e

    # Override HTTP methods to wrap with refresh logic
    # These call super() which goes to API base class

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """GET request with automatic token refresh on 401."""
        if not getattr(self, "_unified_token_mode", False):
            return super().get(path, params, timeout, expected_statuscodes, headers)  # type: ignore[misc]

        def execute() -> Dict[str, Any]:
            auth_headers = self._get_auth_headers()
            return super(UnifiedTokenMixin, self).get(  # type: ignore[misc]
                path, params, timeout, expected_statuscodes, headers=auth_headers
            )

        return self._execute_with_refresh(f"GET {path}", execute)

    def get_content(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bytes:
        """GET content request with automatic token refresh on 401."""
        if not getattr(self, "_unified_token_mode", False):
            return super().get_content(path, params, timeout, expected_statuscodes, headers)  # type: ignore[misc]

        def execute() -> bytes:
            auth_headers = self._get_auth_headers()
            return super(UnifiedTokenMixin, self).get_content(  # type: ignore[misc]
                path, params, timeout, expected_statuscodes, headers=auth_headers
            )

        return self._execute_with_refresh(f"GET(content) {path}", execute)

    def post(
        self,
        path: str,
        body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """POST request with automatic token refresh on 401."""
        if not getattr(self, "_unified_token_mode", False):
            return super().post(path, body, params, timeout, expected_statuscodes, headers)  # type: ignore[misc]

        def execute() -> Dict[str, Any]:
            auth_headers = self._get_auth_headers()
            return super(UnifiedTokenMixin, self).post(  # type: ignore[misc]
                path, body, params, timeout, expected_statuscodes, headers=auth_headers
            )

        return self._execute_with_refresh(f"POST {path}", execute)

    def put(
        self,
        path: str,
        body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """PUT request with automatic token refresh on 401."""
        if not getattr(self, "_unified_token_mode", False):
            return super().put(path, body, params, timeout, expected_statuscodes, headers)  # type: ignore[misc]

        def execute() -> Optional[Dict[str, Any]]:
            auth_headers = self._get_auth_headers()
            return super(UnifiedTokenMixin, self).put(  # type: ignore[misc]
                path, body, params, timeout, expected_statuscodes, headers=auth_headers
            )

        return self._execute_with_refresh(f"PUT {path}", execute)

    def patch(
        self,
        path: str,
        body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """PATCH request with automatic token refresh on 401."""
        if not getattr(self, "_unified_token_mode", False):
            return super().patch(path, body, params, timeout, expected_statuscodes, headers)  # type: ignore[misc]

        def execute() -> Optional[Dict[str, Any]]:
            auth_headers = self._get_auth_headers()
            return super(UnifiedTokenMixin, self).patch(  # type: ignore[misc]
                path, body, params, timeout, expected_statuscodes, headers=auth_headers
            )

        return self._execute_with_refresh(f"PATCH {path}", execute)

    def delete(
        self,
        path: str,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """DELETE request with automatic token refresh on 401."""
        if not getattr(self, "_unified_token_mode", False):
            return super().delete(path, timeout, expected_statuscodes, headers)  # type: ignore[misc]

        def execute() -> None:
            auth_headers = self._get_auth_headers()
            return super(UnifiedTokenMixin, self).delete(  # type: ignore[misc]
                path, timeout, expected_statuscodes, headers=auth_headers
            )

        return self._execute_with_refresh(f"DELETE {path}", execute)

    @property
    def unified_token(self) -> Optional[str]:
        """Return the current unified token if in unified token mode (thread-safe)."""
        if not getattr(self, "_unified_token_mode", False):
            return None
        with self._unified_token_lock:
            return self._unified_token
