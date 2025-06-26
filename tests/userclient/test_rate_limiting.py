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
Tests for rate limiting and exception handling functionality.
"""

import time
from unittest.mock import Mock, patch

import pytest
from ratelimit import RateLimitException
from requests.exceptions import HTTPError

import deepsights
from deepsights.exceptions import AuthenticationError, DeepSightsError, RateLimitError


class TestExceptionAvailability:
    """Test that all custom exceptions are properly available."""

    def test_exceptions_available_at_package_level(self):
        """Test that all custom exceptions are available at the package level."""
        assert hasattr(deepsights, "DeepSightsError")
        assert hasattr(deepsights, "AuthenticationError")
        assert hasattr(deepsights, "RateLimitError")
        assert hasattr(deepsights, "exceptions")

    def test_exception_hierarchy(self):
        """Test that custom exceptions have the correct inheritance hierarchy."""
        assert issubclass(RateLimitError, DeepSightsError)
        assert issubclass(AuthenticationError, DeepSightsError)
        assert issubclass(DeepSightsError, Exception)

    def test_exceptions_module_access(self):
        """Test that exceptions can be accessed through the exceptions module."""
        assert deepsights.exceptions.RateLimitError is RateLimitError
        assert deepsights.exceptions.AuthenticationError is AuthenticationError
        assert deepsights.exceptions.DeepSightsError is DeepSightsError

    def test_rate_limit_error_attributes(self):
        """Test RateLimitError has proper attributes."""
        error = RateLimitError("Test message", retry_after=60)
        assert str(error) == "Test message"
        assert error.retry_after == 60

        # Test without retry_after
        error_no_retry = RateLimitError("Another message")
        assert str(error_no_retry) == "Another message"
        assert error_no_retry.retry_after is None


class TestAnswersV2RateLimiting:
    """Test rate limiting for AnswersV2 resource."""

    def test_create_rate_limit_exception_handling(self, user_client):
        """Test that RateLimitException is properly converted to RateLimitError."""
        # Mock the API post method to raise RateLimitException
        with patch.object(
            user_client.answersV2.api,
            "post",
            side_effect=RateLimitException("Rate limit exceeded", 60),
        ):
            with pytest.raises(RateLimitError) as exc_info:
                user_client.answersV2.create("Test question")

            assert "Answer creation rate limit exceeded" in str(exc_info.value)
            assert exc_info.value.retry_after == 60

    def test_create_and_wait_rate_limit_exception_handling(self, user_client):
        """Test that create_and_wait properly handles rate limit exceptions."""
        # Mock the create method to raise RateLimitException
        with patch.object(
            user_client.answersV2,
            "create",
            side_effect=RateLimitException("Rate limit exceeded", 60),
        ):
            with pytest.raises(RateLimitError) as exc_info:
                user_client.answersV2.create_and_wait("Test question")

            assert "Answer creation rate limit exceeded" in str(exc_info.value)
            assert exc_info.value.retry_after == 60


class TestReportsRateLimiting:
    """Test rate limiting for Reports resource."""

    def test_create_rate_limit_exception_handling(self, user_client):
        """Test that RateLimitException is properly converted to RateLimitError for reports."""
        # Mock the API post method to raise RateLimitException
        with patch.object(
            user_client.reports.api,
            "post",
            side_effect=RateLimitException("Rate limit exceeded", 60),
        ):
            with pytest.raises(RateLimitError) as exc_info:
                user_client.reports.create("Test question")

            assert "Report creation rate limit exceeded" in str(exc_info.value)
            assert exc_info.value.retry_after == 60


class TestPersistent429Handling:
    """Test that persistent 429 errors after retries are converted to RateLimitError."""

    def test_persistent_429_converted_to_rate_limit_error(self):
        """Test that 429 HTTPError after retries is converted to RateLimitError."""
        from deepsights.api.api import _handle_persistent_rate_limit

        # Create a mock function that raises HTTPError with 429
        def mock_func():
            mock_response = Mock()
            mock_response.status_code = 429
            raise HTTPError("429 Too Many Requests", response=mock_response)

        # Apply the decorator
        decorated_func = _handle_persistent_rate_limit(mock_func)

        # Should convert HTTPError to RateLimitError
        with pytest.raises(RateLimitError) as exc_info:
            decorated_func()

        assert "Server rate limit exceeded after retries" in str(exc_info.value)
        assert exc_info.value.retry_after is None  # Server didn't provide retry-after

        # Verify the original exception is preserved as the cause
        assert isinstance(exc_info.value.__cause__, HTTPError)

    def test_non_429_http_errors_passed_through(self):
        """Test that non-429 HTTPErrors are not converted."""
        from deepsights.api.api import _handle_persistent_rate_limit

        def mock_func():
            mock_response = Mock()
            mock_response.status_code = 500
            raise HTTPError("500 Server Error", response=mock_response)

        decorated_func = _handle_persistent_rate_limit(mock_func)

        # Should pass through the original HTTPError
        with pytest.raises(HTTPError) as exc_info:
            decorated_func()

        assert "500 Server Error" in str(exc_info.value)

    def test_non_http_errors_passed_through(self):
        """Test that non-HTTPError exceptions are passed through unchanged."""
        from deepsights.api.api import _handle_persistent_rate_limit

        def mock_func():
            raise ValueError("Some other error")

        decorated_func = _handle_persistent_rate_limit(mock_func)

        with pytest.raises(ValueError) as exc_info:
            decorated_func()

        assert "Some other error" in str(exc_info.value)


class TestAuthenticationErrorHandling:
    """Test authentication error handling."""

    def test_authentication_error_on_401(self):
        """Test that 401 responses are converted to AuthenticationError."""
        from unittest.mock import Mock

        from requests.exceptions import HTTPError

        from deepsights.api.api import _handle_http_error

        # Mock a 401 response
        mock_response = Mock()
        mock_response.status_code = 401

        with pytest.raises(AuthenticationError) as exc_info:
            _handle_http_error(mock_response)

        assert "Invalid API key or insufficient permissions" in str(exc_info.value)

    def test_authentication_error_inheritance(self):
        """Test that AuthenticationError can be caught as DeepSightsError."""
        error = AuthenticationError("Test auth error")

        # Should be catchable as both specific and base exception
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, DeepSightsError)
        assert isinstance(error, Exception)


class TestIntegrationPatterns:
    """Test common integration patterns users would employ."""

    def test_exception_handling_pattern(self):
        """Test common exception handling patterns work as expected."""
        # This tests the documented pattern from the README

        def mock_api_call():
            """Simulate different error conditions."""
            raise RateLimitError("Rate limit exceeded", retry_after=60)

        # Pattern 1: Catch specific exceptions
        with pytest.raises(RateLimitError):
            mock_api_call()

        # Pattern 2: Handle with retry logic
        try:
            mock_api_call()
        except RateLimitError as e:
            assert e.retry_after == 60  # Can access retry information

        def mock_auth_error():
            raise AuthenticationError("Invalid credentials")

        # Pattern 3: Catch base exception
        try:
            mock_auth_error()
        except DeepSightsError:
            pass  # Should catch AuthenticationError as DeepSightsError

    def test_user_friendly_error_messages(self):
        """Test that error messages are user-friendly and informative."""
        rate_error = RateLimitError(
            "Answer creation rate limit exceeded (10 calls per 60 seconds). Please wait before making another request.",
            retry_after=60,
        )

        assert "10 calls per 60 seconds" in str(rate_error)
        assert "Please wait" in str(rate_error)
        assert rate_error.retry_after == 60

        auth_error = AuthenticationError("Invalid API key or insufficient permissions")
        assert "Invalid API key" in str(auth_error)
        assert "permissions" in str(auth_error)

    def test_consistent_rate_limit_handling(self):
        """Test that both client-side and server-side rate limits use RateLimitError."""
        # Client-side rate limit (from ratelimit library)
        client_error = RateLimitError("Client rate limit", retry_after=60)

        # Server-side rate limit (persistent 429)
        server_error = RateLimitError(
            "Server rate limit exceeded after retries", retry_after=None
        )

        # Both should be RateLimitError and catchable the same way
        for error in [client_error, server_error]:
            assert isinstance(error, RateLimitError)
            assert isinstance(error, DeepSightsError)

            # Users can handle both with a single exception type
            try:
                raise error
            except RateLimitError as e:
                assert "rate limit" in str(e).lower()
