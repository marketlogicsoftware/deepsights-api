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
This module contains the user client for the DeepSights API, impersonating a given user.
"""

import logging
import os
import random
import threading
from typing import Callable, Optional

from cachetools import TTLCache

from deepsights.api.api import API, OAuthTokenAPI
from deepsights.api.unified_token import UnifiedTokenMixin
from deepsights.deepsights._mip_identity import MIPIdentityResolver
from deepsights.userclient.resources import (
    AnswerV2Resource,
    DocumentResource,
    ReportResource,
)

logger = logging.getLogger(__name__)
ENDPOINT_BASE = "https://api.deepsights.ai/ds/v1"


#################################################
class UserClient(UnifiedTokenMixin, OAuthTokenAPI):
    """
    This class defined the user client for DeepSights APIs, impersonating a given user.

    Supports three authentication modes (mutually exclusive):
    1. Direct OAuth token (manual refresh)
    2. Auto-refresh mode using email + API key (automatic token refresh via MIP)
    3. Unified token mode with refresh callback (automatic refresh on 401)
    """

    # Class-level static cache for user clients
    _userclients_cache: TTLCache = TTLCache(
        maxsize=int(os.environ.get("DEEPSIGHTS_USERCLIENT_CACHE_MAXSIZE", "100")),
        ttl=int(os.environ.get("DEEPSIGHTS_USERCLIENT_CACHE_TTL", "240")),
    )
    _userclients_lock: threading.RLock = threading.RLock()

    # Instance attribute type hints
    _email: Optional[str]
    _api_key: Optional[str]
    _mip_resolver: Optional[MIPIdentityResolver]
    _refresh_timer: Optional[threading.Timer]

    answersV2: AnswerV2Resource
    reports: ReportResource
    documents: DocumentResource

    #######################################
    def __init__(
        self,
        endpoint_base: Optional[str] = None,
        oauth_token: Optional[str] = None,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        auto_refresh_interval_seconds: int = 600,
        unified_token: Optional[str] = None,
        refresh_callback: Optional[Callable[[], Optional[str]]] = None,
    ) -> None:
        """
        Initializes the API client.

        Args:
            endpoint_base (str, optional): The base URL of the API endpoint.
                If not provided, the default endpoint base will be used.
            oauth_token (str, optional): The OAuth token to be used for authentication.
                If provided, the client will use this token directly without auto-refresh.
            email (str, optional): Email address for auto-refresh mode.
                Required if oauth_token is not provided and unified_token is not provided.
            api_key (str, optional): API key for auto-refresh mode.
                Required if oauth_token is not provided and unified_token is not provided.
            auto_refresh_interval_seconds (int): Interval in seconds for automatic token refresh.
                Only used in auto-refresh mode. Defaults to 600 seconds (10 minutes).
            unified_token (str, optional): Bearer token for unified token authentication.
                Mutually exclusive with oauth_token and email+api_key.
            refresh_callback (Callable, optional): Callback function that returns a new
                token string, or None to signal permanent auth failure (stops retrying).
                Required when using unified_token. The callback MUST implement its own
                timeout to avoid blocking indefinitely.

        Raises:
            ValueError: If not exactly one authentication mode is provided, or if
                unified_token is provided without refresh_callback.
        """
        if endpoint_base is None:
            endpoint_base = ENDPOINT_BASE

        # Count provided auth modes
        mode_count = sum(
            [
                oauth_token is not None,
                (email is not None and api_key is not None),
                unified_token is not None,
            ]
        )

        if mode_count != 1:
            raise ValueError("Must provide exactly one of: 'oauth_token', 'email+api_key', or 'unified_token+refresh_callback'")

        if unified_token is not None:
            # Mode 3: Unified token mode
            if refresh_callback is None:
                raise ValueError("refresh_callback is required when using unified_token")

            self._auto_refresh_enabled = False
            self._email = None
            self._api_key = None
            self._mip_resolver = None
            self._refresh_timer = None

            # Initialize base API class directly (skip OAuthTokenAPI)
            API.__init__(self, endpoint_base=endpoint_base)
            # Initialize unified token mixin
            self.__init_unified_token__(unified_token, refresh_callback)

        elif oauth_token is not None:
            # Mode 1: Direct token mode (existing)
            self._auto_refresh_enabled = False
            self._email = None
            self._api_key = None
            self._mip_resolver = None
            self._refresh_timer = None

            super().__init__(
                endpoint_base=endpoint_base,
                oauth_token=oauth_token,
            )

        else:
            # Mode 2: Auto-refresh mode (existing)
            assert email is not None and api_key is not None

            self._auto_refresh_enabled = True
            self._email = email
            self._api_key = api_key
            self._auto_refresh_interval_seconds = auto_refresh_interval_seconds
            self._refresh_timer = None
            self._refresh_lock = threading.Lock()

            # Initialize MIP resolver and get initial token
            self._mip_resolver = MIPIdentityResolver(api_key=api_key)
            initial_token = self._mip_resolver.get_oauth_token(email)

            if not initial_token:
                raise ValueError(f"Failed to obtain initial OAuth token for email: {email}")

            interval_minutes = auto_refresh_interval_seconds / 60
            logger.info(f"Auto-refresh enabled for user {email} with {interval_minutes:.1f}-minute intervals")

            super().__init__(
                endpoint_base=endpoint_base,
                oauth_token=initial_token,
            )

        # Initialize resource classes
        self.answersV2 = AnswerV2Resource(self)
        self.reports = ReportResource(self)
        self.documents = DocumentResource(self)

        # Start auto-refresh if enabled (Mode 2 only)
        if self._auto_refresh_enabled:
            self._schedule_token_refresh()

    #######################################
    def _refresh_oauth_token(self) -> None:
        """
        Refreshes the OAuth token using the MIP identity resolver.

        This method is called automatically in auto-refresh mode.
        It updates the session headers with the new token.
        """
        if not self._auto_refresh_enabled:
            logger.warning("Token refresh attempted but auto-refresh is not enabled")
            return

        try:
            with self._refresh_lock:
                logger.debug(f"Refreshing OAuth token for user {self._email}")

                # Ensure resolver and email are initialized in auto-refresh mode
                assert self._mip_resolver is not None
                assert self._email is not None
                new_token = self._mip_resolver.get_oauth_token(self._email)

                if new_token:
                    # Update the stored token
                    self._oauth_token = new_token

                    # Update session headers
                    self._session.headers.update({"Authorization": f"Bearer {new_token}"})

                    logger.info(f"Successfully refreshed OAuth token for user {self._email}")
                else:
                    logger.error(f"Failed to refresh OAuth token for user {self._email}: No token returned")

        except Exception as e:  # Keep broad catch to avoid crashing background timer
            logger.exception("Error refreshing OAuth token for user %s: %s", self._email, str(e))
        finally:
            # Schedule the next refresh regardless of success/failure
            if self._auto_refresh_enabled:
                self._schedule_token_refresh()

    #######################################
    def _schedule_token_refresh(self) -> None:
        """
        Schedules the next token refresh.
        """
        if not self._auto_refresh_enabled:
            return

        # Cancel any existing timer
        if hasattr(self, "_refresh_timer") and self._refresh_timer:
            self._refresh_timer.cancel()

        # Schedule next refresh
        # Apply small jitter (+/-10%) to avoid synchronized refresh storms
        jitter_pct = 0.1
        interval = max(
            1.0,
            self._auto_refresh_interval_seconds + self._auto_refresh_interval_seconds * random.uniform(-jitter_pct, jitter_pct),
        )

        self._refresh_timer = threading.Timer(interval, self._refresh_oauth_token)
        self._refresh_timer.daemon = True  # Allow program to exit even if timer is running
        self._refresh_timer.start()

        logger.debug("Scheduled next token refresh in %.1f minutes (with jitter)", interval / 60)

    #######################################
    def stop_auto_refresh(self) -> None:
        """
        Stops the automatic token refresh.

        This method can be called to manually stop the auto-refresh mechanism.
        """
        try:
            if getattr(self, "_auto_refresh_enabled", False):
                timer = getattr(self, "_refresh_timer", None)
                if isinstance(timer, threading.Timer):
                    timer.cancel()
        finally:
            if getattr(self, "_auto_refresh_enabled", False):
                self._auto_refresh_enabled = False
                logger.info("Auto-refresh stopped for user %s", self._email)

    #######################################
    def manual_token_refresh(self) -> bool:
        """
        Manually triggers a token refresh.

        This method can be called to immediately refresh the token
        without waiting for the scheduled refresh.

        Returns:
            bool: True if token was successfully refreshed, False otherwise.

        Raises:
            ValueError: If auto-refresh is not enabled.
        """
        if not self._auto_refresh_enabled:
            raise ValueError("Manual token refresh is only available in auto-refresh mode")

        try:
            old_token = self._oauth_token
            self._refresh_oauth_token()
            return self._oauth_token != old_token and self._oauth_token is not None
        except Exception as e:
            logger.exception("Manual token refresh failed: %s", str(e))
            return False

    #######################################
    def get_token_info(self) -> dict:
        """
        Returns information about the current token and refresh configuration.

        Returns:
            dict: Dictionary containing token info and refresh settings.
        """
        # Check for token - could be _oauth_token (OAuth mode) or _unified_token (unified mode)
        has_token = bool(getattr(self, "_oauth_token", None) or getattr(self, "_unified_token", None))
        return {
            "auto_refresh_enabled": self._auto_refresh_enabled,
            "email": self._email if self._auto_refresh_enabled else None,
            "refresh_interval_seconds": getattr(self, "_auto_refresh_interval_seconds", None),
            "has_token": has_token,
        }

    #######################################
    def close(self) -> None:
        """
        Stop auto-refresh (if enabled) and close the underlying HTTP session.
        """
        try:
            if getattr(self, "_auto_refresh_enabled", False):
                self.stop_auto_refresh()
        finally:
            super().close()

    #######################################
    @staticmethod
    def cache_info() -> dict:
        """
        Return userclient cache configuration and current size.
        """
        cache = UserClient._userclients_cache
        return {"maxsize": cache.maxsize, "ttl": cache.ttl, "currsize": len(cache)}

    #######################################
    @staticmethod
    def cache_clear() -> None:
        """Clear the userclient cache entirely."""
        with UserClient._userclients_lock:
            UserClient._userclients_cache.clear()

    #######################################
    @staticmethod
    def cache_invalidate(user_email: str) -> None:
        """Remove a specific user from the userclient cache (email normalized)."""
        if not user_email:
            return
        email = user_email.lower().strip()
        with UserClient._userclients_lock:
            UserClient._userclients_cache.pop(email, None)

    #######################################
    @staticmethod
    def get_userclient(user_email: str, mip_api_key: str, endpoint_base: Optional[str] = None) -> "UserClient":
        """
        Retrieves a user client for the given user.

        Args:
            user_email (str): The email of the user to impersonate.
            mip_api_key (str): The API key for the MIP API.
            endpoint_base (str, optional): The base URL of the API endpoint.
                If not provided, the default endpoint base will be used.

        Returns:
            UserClient: The user client for the given user. Will be cached.

        Raises:
            ValueError: If the user is not found.
        """
        # normalize the email
        user_email = user_email.lower().strip()

        if endpoint_base is None:
            endpoint_base = ENDPOINT_BASE

        # thread-safe cache access
        with UserClient._userclients_lock:
            # create the user client if it doesn't exist
            if user_email not in UserClient._userclients_cache:
                mip_identity_resolver = MIPIdentityResolver(mip_api_key)
                oauth_token = mip_identity_resolver.get_oauth_token(user_email)
                if not oauth_token:
                    raise ValueError(f"User not found: {user_email}")

                UserClient._userclients_cache[user_email] = UserClient(oauth_token=oauth_token, endpoint_base=endpoint_base)

            return UserClient._userclients_cache[user_email]

    #######################################
    @staticmethod
    def get_userclient_by_token(oauth_token: str, endpoint_base: Optional[str] = None) -> "UserClient":
        """
        Retrieves a user client for the given OAuth token.

        Args:
            oauth_token (str): The OAuth token to be used for authentication.
            endpoint_base (str, optional): The base URL of the API endpoint.
                If not provided, the default endpoint base will be used.
        """
        return UserClient(oauth_token=oauth_token, endpoint_base=endpoint_base)

    #######################################
    @classmethod
    def with_unified_token(
        cls,
        unified_token: str,
        refresh_callback: Callable[[], Optional[str]],
        endpoint_base: Optional[str] = None,
    ) -> "UserClient":
        """
        Alternative constructor for unified token authentication.

        Args:
            unified_token: Bearer token string for authentication.
            refresh_callback: Callback function that returns a new token on 401,
                or None to signal permanent failure (stops retrying). Must implement
                its own timeout to avoid blocking indefinitely.
            endpoint_base: Optional custom endpoint base URL.

        Returns:
            UserClient instance configured with unified token authentication.
        """
        return cls(
            unified_token=unified_token,
            refresh_callback=refresh_callback,
            endpoint_base=endpoint_base,
        )

    #######################################
    def __del__(self) -> None:
        """
        Cleanup method to stop auto-refresh when the object is destroyed.
        """
        if hasattr(self, "_auto_refresh_enabled") and self._auto_refresh_enabled:
            self.stop_auto_refresh()
