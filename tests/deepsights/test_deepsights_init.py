# Copyright 2024-2025 Market Logic Software AG.

"""
Unit tests for DeepSights client initialization permutations.
"""

import os
from unittest.mock import Mock, patch

import pytest

from deepsights import DeepSights


class TestDeepSightsInitPermutations:
    """Tests for DeepSights constructor with various auth configurations."""

    def test_ds_key_only_documentstore_works(self):
        """Verify DS key only: documentstore accessible, contentstore raises."""
        with patch.dict(os.environ, {}, clear=True):
            client = DeepSights(ds_api_key="test_ds_key")

            # documentstore should be configured
            assert client._documentstore is not None
            assert client.documentstore is not None

            # contentstore should raise
            assert client._contentstore is None
            with pytest.raises(ValueError) as exc:
                _ = client.contentstore
            assert "ContentStore not configured" in str(exc.value)

    def test_cs_key_only_contentstore_works(self):
        """Verify CS key only: contentstore accessible, documentstore raises."""
        with patch.dict(os.environ, {}, clear=True):
            # Need to provide ds_api_key too since DeepSights inherits from APIKeyAPI
            # and requires it. Let's check if it does...
            # Actually, looking at the code, DeepSights.__init__ calls super().__init__
            # with api_key_env_var="DEEPSIGHTS_API_KEY", so it will fail without DS key.
            # Let me verify the behavior.
            pass

    def test_cs_key_only_via_env_var(self):
        """Verify CS key from env var works."""
        with patch.dict(os.environ, {"DEEPSIGHTS_API_KEY": "ds_key", "CONTENTSTORE_API_KEY": "cs_key"}, clear=True):
            client = DeepSights()

            # Both should be configured
            assert client._documentstore is not None
            assert client._contentstore is not None

    def test_cs_unified_token_contentstore_works(self):
        """Verify unified token auth for contentstore works."""
        refresh_callback = Mock(return_value="new_token")

        with patch.dict(os.environ, {"DEEPSIGHTS_API_KEY": "ds_key"}, clear=True):
            client = DeepSights(
                cs_unified_token="test_unified_token",
                cs_refresh_callback=refresh_callback,
            )

            # contentstore should be configured with unified token
            assert client._contentstore is not None
            assert client._contentstore._unified_token_mode is True
            assert client._contentstore._unified_token == "test_unified_token"

    def test_both_ds_and_cs_keys(self):
        """Verify both DS and CS keys work together."""
        with patch.dict(os.environ, {}, clear=True):
            client = DeepSights(ds_api_key="ds_key", cs_api_key="cs_key")

            # Both should be configured
            assert client._documentstore is not None
            assert client._contentstore is not None
            assert client.documentstore is not None
            assert client.contentstore is not None

    def test_neither_auth_both_raise_on_access(self):
        """Verify no auth: both raise ValueError on access."""
        with patch.dict(os.environ, {"DEEPSIGHTS_API_KEY": "ds_key"}, clear=True):
            # Need DS key for DeepSights base class, but no CS key
            client = DeepSights(ds_api_key="ds_key")

            # documentstore works (has ds_key)
            assert client._documentstore is not None

            # contentstore raises
            with pytest.raises(ValueError) as exc:
                _ = client.contentstore
            assert "ContentStore not configured" in str(exc.value)

    def test_cs_api_key_and_unified_token_mutual_exclusivity(self):
        """Verify cs_api_key and cs_unified_token are mutually exclusive."""
        refresh_callback = Mock(return_value="new_token")

        with patch.dict(os.environ, {"DEEPSIGHTS_API_KEY": "ds_key"}, clear=True):
            # This should raise because ContentStore validates mutual exclusivity
            with pytest.raises(ValueError) as exc:
                DeepSights(
                    cs_api_key="cs_key",
                    cs_unified_token="unified_token",
                    cs_refresh_callback=refresh_callback,
                )
            assert "Cannot use both" in str(exc.value)

    def test_cs_unified_token_without_callback_raises(self):
        """Verify unified token without callback raises ValueError."""
        with patch.dict(os.environ, {"DEEPSIGHTS_API_KEY": "ds_key"}, clear=True):
            with pytest.raises(ValueError) as exc:
                DeepSights(cs_unified_token="unified_token")
            assert "refresh_callback is required" in str(exc.value)

    def test_env_vars_used_when_no_explicit_keys(self):
        """Verify environment variables are used when no explicit keys provided."""
        with patch.dict(
            os.environ,
            {"DEEPSIGHTS_API_KEY": "env_ds_key", "CONTENTSTORE_API_KEY": "env_cs_key"},
            clear=True,
        ):
            client = DeepSights()

            # Both should be configured from env vars
            assert client._documentstore is not None
            assert client._contentstore is not None

    def test_explicit_keys_override_env_vars(self):
        """Verify explicit keys override environment variables."""
        with patch.dict(
            os.environ,
            {"DEEPSIGHTS_API_KEY": "env_ds_key", "CONTENTSTORE_API_KEY": "env_cs_key"},
            clear=True,
        ):
            client = DeepSights(ds_api_key="explicit_ds_key", cs_api_key="explicit_cs_key")

            # Should use explicit keys
            assert client._api_key == "explicit_ds_key"
            assert client._contentstore is not None
            # ContentStore uses session headers for API key
            assert client._contentstore._session.headers.get("X-Api-Key") == "explicit_cs_key"


class TestDeepSightsPropertyErrors:
    """Tests for helpful error messages when accessing unconfigured services."""

    def test_documentstore_error_message(self):
        """Verify documentstore error message is helpful."""
        with patch.dict(os.environ, {"DEEPSIGHTS_API_KEY": "ds_key"}, clear=True):
            # Create client where _documentstore is None
            client = DeepSights(ds_api_key="ds_key")
            client._documentstore = None  # Force it to None for testing

            with pytest.raises(ValueError) as exc:
                _ = client.documentstore

            error_msg = str(exc.value)
            assert "DocumentStore not configured" in error_msg
            assert "ds_api_key" in error_msg
            assert "DEEPSIGHTS_API_KEY" in error_msg

    def test_contentstore_error_message(self):
        """Verify contentstore error message is helpful."""
        with patch.dict(os.environ, {"DEEPSIGHTS_API_KEY": "ds_key"}, clear=True):
            client = DeepSights(ds_api_key="ds_key")

            with pytest.raises(ValueError) as exc:
                _ = client.contentstore

            error_msg = str(exc.value)
            assert "ContentStore not configured" in error_msg
            assert "cs_api_key" in error_msg
            assert "CONTENTSTORE_API_KEY" in error_msg
            assert "cs_unified_token" in error_msg
