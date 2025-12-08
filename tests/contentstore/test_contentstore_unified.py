# Copyright 2024-2025 Market Logic Software AG.

"""
Unit tests for ContentStore unified token authentication.
"""

import os
from unittest.mock import Mock, patch

import pytest

from deepsights.contentstore import ContentStore


class TestContentStoreConstructorValidation:
    """Tests for ContentStore constructor validation."""

    def test_api_key_and_unified_token_mutually_exclusive(self):
        """Verify ValueError when both auth methods provided."""
        with pytest.raises(ValueError) as exc:
            ContentStore(
                api_key="test_key",
                unified_token="test_token",
                refresh_callback=lambda: "new_token",
            )

        assert "Cannot use both" in str(exc.value)

    def test_unified_token_requires_refresh_callback(self):
        """Verify ValueError when unified_token without callback."""
        with pytest.raises(ValueError) as exc:
            ContentStore(unified_token="test_token")

        assert "refresh_callback is required" in str(exc.value)

    def test_no_auth_provided_raises_error(self):
        """Verify ValueError when neither auth method provided."""
        # Make sure env var is not set
        with patch.dict(os.environ, {}, clear=True):
            # Need to clear CONTENTSTORE_API_KEY if present
            env_without_key = {k: v for k, v in os.environ.items() if k != "CONTENTSTORE_API_KEY"}
            with patch.dict(os.environ, env_without_key, clear=True):
                with pytest.raises(ValueError) as exc:
                    ContentStore()

                assert "Must provide either" in str(exc.value)


class TestContentStoreUnifiedTokenMode:
    """Tests for ContentStore unified token mode."""

    def test_unified_token_mode_initialization(self):
        """Verify unified token mode sets up correctly."""
        refresh_callback = Mock(return_value="new_token")
        client = ContentStore(
            unified_token="initial_token",
            refresh_callback=refresh_callback,
        )

        assert client._unified_token_mode is True
        assert client._unified_token == "initial_token"
        # Token is passed per-request, NOT on session headers (thread-safety)
        assert "Authorization" not in client._session.headers
        assert client._get_auth_headers() == {"Authorization": "Bearer initial_token"}
        # Resources should be initialized
        assert client.news is not None
        assert client.secondary is not None

    def test_with_unified_token_classmethod(self):
        """Verify alternative constructor works correctly."""
        refresh_callback = Mock(return_value="new_token")
        client = ContentStore.with_unified_token(
            unified_token="test_token",
            refresh_callback=refresh_callback,
        )

        assert client._unified_token_mode is True
        assert client._unified_token == "test_token"

    def test_with_unified_token_custom_endpoint(self):
        """Verify custom endpoint is used with unified token."""
        refresh_callback = Mock(return_value="new_token")
        client = ContentStore.with_unified_token(
            unified_token="test_token",
            refresh_callback=refresh_callback,
            endpoint_base="https://custom.endpoint.com/api/",
        )

        assert client._endpoint_base == "https://custom.endpoint.com/api/"


class TestContentStoreAPIKeyModeBackwardCompatibility:
    """Tests for backward compatibility with API key mode."""

    def test_existing_api_key_mode_unchanged(self):
        """Verify backward compatibility with API key auth."""
        client = ContentStore(api_key="test_api_key")

        # Should NOT be in unified token mode
        assert getattr(client, "_unified_token_mode", False) is False
        # Should have API key header
        assert client._session.headers.get("X-Api-Key") == "test_api_key"
        # Resources should be initialized
        assert client.news is not None
        assert client.secondary is not None

    def test_api_key_from_env_var(self):
        """Verify API key can be read from environment variable."""
        with patch.dict(os.environ, {"CONTENTSTORE_API_KEY": "env_api_key"}):
            client = ContentStore()

            assert getattr(client, "_unified_token_mode", False) is False
            assert client._session.headers.get("X-Api-Key") == "env_api_key"


class TestContentStoreUnifiedTokenRefresh:
    """Tests for ContentStore unified token refresh functionality."""

    def test_401_triggers_refresh_callback(self):
        """Verify 401 triggers refresh callback."""
        call_count = 0
        refresh_call_count = 0

        def refresh_callback():
            nonlocal refresh_call_count
            refresh_call_count += 1
            return "refreshed_token"

        client = ContentStore(
            unified_token="initial_token",
            refresh_callback=refresh_callback,
        )

        # Mock the session get method
        def mock_get(url, params=None, timeout=None, headers=None):
            nonlocal call_count
            call_count += 1

            class MockResponse:
                def __init__(self, status_code, json_data=None):
                    self.status_code = status_code
                    self._json_data = json_data or {}

                def raise_for_status(self):
                    if self.status_code >= 400:
                        from requests.exceptions import HTTPError

                        raise HTTPError(f"{self.status_code}", response=self)

                def json(self):
                    return self._json_data

            if call_count == 1:
                return MockResponse(401)
            return MockResponse(200, {"data": "value"})

        client._session.get = mock_get  # type: ignore[method-assign]

        result = client.get("/test")

        assert result == {"data": "value"}
        assert call_count == 2
        assert refresh_call_count == 1
        assert client._unified_token == "refreshed_token"
