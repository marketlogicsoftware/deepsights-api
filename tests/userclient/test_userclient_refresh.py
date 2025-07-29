"""
Tests for UserClient automatic token refresh functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from deepsights.userclient.userclient import UserClient


class TestUserClientRefresh:
    """Test cases for UserClient automatic token refresh functionality."""

    def test_direct_token_mode(self):
        """Test UserClient in direct token mode (no auto-refresh)."""
        test_token = "test_oauth_token_123"

        client = UserClient(oauth_token=test_token)

        # Verify direct mode is set correctly
        token_info = client.get_token_info()
        assert not token_info["auto_refresh_enabled"]
        assert token_info["email"] is None
        assert token_info["refresh_interval_seconds"] is None
        assert token_info["has_token"] is True

        # Verify token is set correctly
        assert client._oauth_token == test_token
        assert not client._auto_refresh_enabled

    def test_auto_refresh_mode_initialization(self):
        """Test UserClient initialization in auto-refresh mode."""
        test_email = "test@example.com"
        test_api_key = "test_api_key_123"
        test_token = "auto_refresh_token_456"
        test_interval = 30  # 30 seconds for testing

        with patch(
            "deepsights.userclient.userclient.MIPIdentityResolver"
        ) as mock_resolver_class:
            # Mock the MIP resolver
            mock_resolver = MagicMock()
            mock_resolver.get_oauth_token.return_value = test_token
            mock_resolver_class.return_value = mock_resolver

            client = UserClient(
                email=test_email,
                api_key=test_api_key,
                auto_refresh_interval_seconds=test_interval,
            )

            # Verify auto-refresh mode is set correctly
            token_info = client.get_token_info()
            assert token_info["auto_refresh_enabled"]
            assert token_info["email"] == test_email
            assert token_info["refresh_interval_seconds"] == test_interval
            assert token_info["has_token"] is True

            # Verify token is set correctly
            assert client._oauth_token == test_token
            assert client._auto_refresh_enabled
            assert client._email == test_email
            assert client._auto_refresh_interval_seconds == test_interval

    def test_default_refresh_interval(self):
        """Test that default refresh interval is 600 seconds (10 minutes)."""
        test_email = "test@example.com"
        test_api_key = "test_api_key_123"
        test_token = "test_token_456"

        with patch(
            "deepsights.userclient.userclient.MIPIdentityResolver"
        ) as mock_resolver_class:
            # Mock the MIP resolver
            mock_resolver = MagicMock()
            mock_resolver.get_oauth_token.return_value = test_token
            mock_resolver_class.return_value = mock_resolver

            client = UserClient(email=test_email, api_key=test_api_key)

            # Verify default interval is 600 seconds (10 minutes)
            token_info = client.get_token_info()
            assert token_info["refresh_interval_seconds"] == 600

    def test_invalid_initialization_parameters(self):
        """Test that UserClient raises appropriate errors for invalid parameters."""

        # Test with no parameters
        with pytest.raises(ValueError, match="Must provide either 'oauth_token'"):
            UserClient()

        # Test with only email (missing api_key)
        with pytest.raises(ValueError, match="Must provide either 'oauth_token'"):
            UserClient(email="test@example.com")

        # Test with only api_key (missing email)
        with pytest.raises(ValueError, match="Must provide either 'oauth_token'"):
            UserClient(api_key="test_api_key")

    def test_failed_initial_token_retrieval(self):
        """Test behavior when initial token retrieval fails."""
        test_email = "nonexistent@example.com"
        test_api_key = "test_api_key_123"

        with patch(
            "deepsights.userclient.userclient.MIPIdentityResolver"
        ) as mock_resolver_class:
            # Mock the MIP resolver to return None (failed token retrieval)
            mock_resolver = MagicMock()
            mock_resolver.get_oauth_token.return_value = None
            mock_resolver_class.return_value = mock_resolver

            with pytest.raises(
                ValueError, match="Failed to obtain initial OAuth token"
            ):
                UserClient(email=test_email, api_key=test_api_key)

    def test_manual_token_refresh(self):
        """Test manual token refresh functionality."""
        test_email = "test@example.com"
        test_api_key = "test_api_key_123"
        initial_token = "initial_token_123"
        refreshed_token = "refreshed_token_456"
        test_interval = 5  # 5 seconds for testing

        with patch(
            "deepsights.userclient.userclient.MIPIdentityResolver"
        ) as mock_resolver_class:
            # Mock the MIP resolver
            mock_resolver = MagicMock()
            mock_resolver.get_oauth_token.side_effect = [initial_token, refreshed_token]
            mock_resolver_class.return_value = mock_resolver

            client = UserClient(
                email=test_email,
                api_key=test_api_key,
                auto_refresh_interval_seconds=test_interval,
            )

            # Verify initial token
            assert client._oauth_token == initial_token

            # Perform manual refresh
            success = client.manual_token_refresh()

            # Verify refresh was successful
            assert success
            assert client._oauth_token == refreshed_token
            assert (
                "Bearer " + refreshed_token in client._session.headers["Authorization"]
            )

    def test_manual_refresh_in_direct_mode_raises_error(self):
        """Test that manual refresh raises error in direct token mode."""
        client = UserClient(oauth_token="test_token_123")

        with pytest.raises(
            ValueError,
            match="Manual token refresh is only available in auto-refresh mode",
        ):
            client.manual_token_refresh()

    def test_stop_auto_refresh(self):
        """Test stopping auto-refresh functionality."""
        test_email = "test@example.com"
        test_api_key = "test_api_key_123"
        test_token = "test_token_123"
        test_interval = 2  # 2 seconds for testing

        with patch(
            "deepsights.userclient.userclient.MIPIdentityResolver"
        ) as mock_resolver_class:
            # Mock the MIP resolver
            mock_resolver = MagicMock()
            mock_resolver.get_oauth_token.return_value = test_token
            mock_resolver_class.return_value = mock_resolver

            client = UserClient(
                email=test_email,
                api_key=test_api_key,
                auto_refresh_interval_seconds=test_interval,
            )

            # Verify auto-refresh is initially enabled
            assert client._auto_refresh_enabled

            # Stop auto-refresh
            client.stop_auto_refresh()

            # Verify auto-refresh is disabled
            assert not client._auto_refresh_enabled

    def test_custom_refresh_intervals(self):
        """Test different custom refresh intervals."""
        test_email = "test@example.com"
        test_api_key = "test_api_key_123"
        test_token = "test_token_123"

        # Test various intervals in seconds
        test_intervals = [1, 10, 60, 300, 1800]  # 1s, 10s, 1min, 5min, 30min

        with patch(
            "deepsights.userclient.userclient.MIPIdentityResolver"
        ) as mock_resolver_class:
            # Mock the MIP resolver
            mock_resolver = MagicMock()
            mock_resolver.get_oauth_token.return_value = test_token
            mock_resolver_class.return_value = mock_resolver

            for interval in test_intervals:
                client = UserClient(
                    email=test_email,
                    api_key=test_api_key,
                    auto_refresh_interval_seconds=interval,
                )

                token_info = client.get_token_info()
                assert token_info["refresh_interval_seconds"] == interval

                # Clean up
                client.stop_auto_refresh()

    def test_backward_compatibility(self):
        """Test that existing code using direct oauth_token still works."""
        test_token = "existing_code_token_123"

        # This should work exactly as before
        client = UserClient(oauth_token=test_token)

        # Verify all resource classes are still initialized
        assert hasattr(client, "answersV2")
        assert hasattr(client, "reports")
        assert hasattr(client, "search")
        assert hasattr(client, "documents")

        # Verify token is set
        assert client._oauth_token == test_token

    def test_refresh_scheduling(self):
        """Test that refresh is properly scheduled."""
        test_email = "test@example.com"
        test_api_key = "test_api_key_123"
        test_token = "test_token_123"
        test_interval = 1  # 1 second for testing

        with patch(
            "deepsights.userclient.userclient.MIPIdentityResolver"
        ) as mock_resolver_class:
            # Mock the MIP resolver
            mock_resolver = MagicMock()
            mock_resolver.get_oauth_token.return_value = test_token
            mock_resolver_class.return_value = mock_resolver

            client = UserClient(
                email=test_email,
                api_key=test_api_key,
                auto_refresh_interval_seconds=test_interval,
            )

            # Verify timer is created and running
            assert hasattr(client, "_refresh_timer")
            assert client._refresh_timer is not None
            assert client._refresh_timer.is_alive()

            # Clean up
            client.stop_auto_refresh()


if __name__ == "__main__":
    pytest.main([__file__])
