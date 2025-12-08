# Copyright 2024-2025 Market Logic Software AG.

"""
Unit tests for UserClient unified token authentication.
"""

from unittest.mock import Mock, patch

import pytest

from deepsights.userclient import UserClient


class TestUserClientConstructorValidation:
    """Tests for UserClient constructor validation."""

    def test_three_modes_mutually_exclusive(self):
        """Verify only one auth mode can be used."""
        # oauth_token + unified_token
        with pytest.raises(ValueError) as exc:
            UserClient(
                oauth_token="test_oauth",
                unified_token="test_unified",
                refresh_callback=lambda: "new",
            )
        assert "exactly one of" in str(exc.value)

        # email+api_key + unified_token
        with pytest.raises(ValueError) as exc:
            UserClient(
                email="test@example.com",
                api_key="test_key",
                unified_token="test_unified",
                refresh_callback=lambda: "new",
            )
        assert "exactly one of" in str(exc.value)

    def test_unified_token_requires_refresh_callback(self):
        """Verify ValueError when unified_token without callback."""
        with pytest.raises(ValueError) as exc:
            UserClient(unified_token="test_token")

        assert "refresh_callback is required" in str(exc.value)

    def test_no_auth_provided_raises_error(self):
        """Verify ValueError when no auth method provided."""
        with pytest.raises(ValueError) as exc:
            UserClient()

        assert "exactly one of" in str(exc.value)


class TestUserClientUnifiedTokenMode:
    """Tests for UserClient unified token mode."""

    def test_unified_token_mode_initialization(self):
        """Verify unified token mode sets up correctly."""
        refresh_callback = Mock(return_value="new_token")
        client = UserClient(
            unified_token="initial_token",
            refresh_callback=refresh_callback,
        )

        assert client._unified_token_mode is True
        assert client._unified_token == "initial_token"
        # Token is passed per-request, NOT on session headers (thread-safety)
        assert "Authorization" not in client._session.headers
        assert client._get_auth_headers() == {"Authorization": "Bearer initial_token"}
        assert client._auto_refresh_enabled is False
        assert client._email is None
        # Resources should be initialized
        assert client.answersV2 is not None
        assert client.reports is not None
        assert client.documents is not None

    def test_with_unified_token_classmethod(self):
        """Verify alternative constructor works correctly."""
        refresh_callback = Mock(return_value="new_token")
        client = UserClient.with_unified_token(
            unified_token="test_token",
            refresh_callback=refresh_callback,
        )

        assert client._unified_token_mode is True
        assert client._unified_token == "test_token"

    def test_with_unified_token_custom_endpoint(self):
        """Verify custom endpoint is used with unified token."""
        refresh_callback = Mock(return_value="new_token")
        client = UserClient.with_unified_token(
            unified_token="test_token",
            refresh_callback=refresh_callback,
            endpoint_base="https://custom.endpoint.com/api/",
        )

        assert client._endpoint_base == "https://custom.endpoint.com/api/"


class TestUserClientOAuthModeBackwardCompatibility:
    """Tests for backward compatibility with existing auth modes."""

    def test_existing_oauth_mode_unchanged(self):
        """Verify backward compatibility with direct token."""
        client = UserClient(oauth_token="test_oauth_token")

        # Should NOT be in unified token mode
        assert getattr(client, "_unified_token_mode", False) is False
        # Should have Authorization header from OAuthTokenAPI
        assert client._session.headers.get("Authorization") == "Bearer test_oauth_token"
        assert client._auto_refresh_enabled is False
        # Resources should be initialized
        assert client.answersV2 is not None
        assert client.reports is not None
        assert client.documents is not None

    def test_existing_auto_refresh_mode_unchanged(self):
        """Verify backward compatibility with MIP auto-refresh."""
        # Mock the MIPIdentityResolver to avoid actual API calls
        with patch("deepsights.userclient.userclient.MIPIdentityResolver") as MockResolver:
            mock_resolver = Mock()
            mock_resolver.get_oauth_token.return_value = "mip_oauth_token"
            MockResolver.return_value = mock_resolver

            client = UserClient(
                email="test@example.com",
                api_key="test_api_key",
                auto_refresh_interval_seconds=300,
            )

            # Should NOT be in unified token mode
            assert getattr(client, "_unified_token_mode", False) is False
            # Should be in auto-refresh mode
            assert client._auto_refresh_enabled is True
            assert client._email == "test@example.com"
            # Should have Authorization header
            assert client._session.headers.get("Authorization") == "Bearer mip_oauth_token"

            # Cleanup
            client.stop_auto_refresh()


class TestUserClientUnifiedTokenRefresh:
    """Tests for UserClient unified token refresh functionality."""

    def test_401_triggers_refresh_callback(self):
        """Verify 401 triggers refresh callback."""
        call_count = 0
        refresh_call_count = 0

        def refresh_callback():
            nonlocal refresh_call_count
            refresh_call_count += 1
            return "refreshed_token"

        client = UserClient(
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


class TestUserClientGetTokenInfo:
    """Tests for get_token_info method with unified token mode."""

    def test_get_token_info_unified_mode(self):
        """Verify get_token_info returns correct info in unified mode."""
        refresh_callback = Mock(return_value="new_token")
        client = UserClient(
            unified_token="test_token",
            refresh_callback=refresh_callback,
        )

        info = client.get_token_info()

        assert info["auto_refresh_enabled"] is False
        assert info["email"] is None
        assert info["has_token"] is True

    def test_get_token_info_oauth_mode(self):
        """Verify get_token_info returns correct info in oauth mode."""
        client = UserClient(oauth_token="test_oauth_token")

        info = client.get_token_info()

        assert info["auto_refresh_enabled"] is False
        assert info["email"] is None
        assert info["has_token"] is True
