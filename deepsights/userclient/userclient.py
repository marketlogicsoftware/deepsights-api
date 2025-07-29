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
import threading
from typing import Optional

from cachetools import TTLCache

from deepsights.api.api import OAuthTokenAPI
from deepsights.deepsights._mip_identity import MIPIdentityResolver
from deepsights.userclient.resources import (
    AnswerV2Resource,
    DocumentResource,
    ReportResource,
    SearchResource,
)

logger = logging.getLogger(__name__)
ENDPOINT_BASE = "https://api.deepsights.ai/ds/v1"

#################################################
class UserClient(OAuthTokenAPI):
    """
    This class defined the user client for DeepSights APIs, impersonating a given user.

    Supports two modes:
    1. Direct OAuth token (manual refresh)
    2. Auto-refresh mode using email + API key (automatic token refresh)
    """

    # Class-level static cache for user clients
    _userclients_cache: TTLCache = TTLCache(maxsize=100, ttl=240)
    _userclients_lock: threading.RLock = threading.RLock()

    answersV2: AnswerV2Resource
    reports: ReportResource
    search: SearchResource
    documents: DocumentResource

    #######################################
    def __init__(
        self,
        endpoint_base: Optional[str] = None,
        oauth_token: Optional[str] = None,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        auto_refresh_interval_seconds: int = 600,
    ) -> None:
        """
        Initializes the API client.

        Args:
            endpoint_base (str, optional): The base URL of the API endpoint.
                If not provided, the default endpoint base will be used.
            oauth_token (str, optional): The OAuth token to be used for authentication.
                If provided, the client will use this token directly without auto-refresh.
            email (str, optional): Email address for auto-refresh mode.
                Required if oauth_token is not provided.
            api_key (str, optional): API key for auto-refresh mode.
                Required if oauth_token is not provided.
            auto_refresh_interval_seconds (int): Interval in seconds for automatic token refresh.
                Only used in auto-refresh mode. Defaults to 600 seconds (10 minutes).

        Raises:
            ValueError: If neither oauth_token nor (email + api_key) is provided.
        """
        if endpoint_base is None:
            endpoint_base = ENDPOINT_BASE

        # Validate input parameters
        if oauth_token:
            # Direct token mode
            self._auto_refresh_enabled = False
            self._email = None
            self._api_key = None
            self._mip_resolver = None
            initial_token = oauth_token
        elif email and api_key:
            # Auto-refresh mode
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
                raise ValueError(
                    f"Failed to obtain initial OAuth token for email: {email}"
                )

            interval_minutes = auto_refresh_interval_seconds / 60
            logger.info(
                f"Auto-refresh enabled for user {email} with {interval_minutes:.1f}-minute intervals"
            )
        else:
            raise ValueError(
                "Must provide either 'oauth_token' for direct mode or both 'email' and 'api_key' for auto-refresh mode"
            )

        # Initialize parent class with the token
        super().__init__(
            endpoint_base=endpoint_base,
            oauth_token=initial_token,
        )

        # Initialize resource classes
        self.answersV2 = AnswerV2Resource(self)
        self.reports = ReportResource(self)
        self.search = SearchResource(self)
        self.documents = DocumentResource(self)

        # Start auto-refresh if enabled
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

                new_token = self._mip_resolver.get_oauth_token(self._email)

                if new_token:
                    # Update the stored token
                    self._oauth_token = new_token

                    # Update session headers
                    self._session.headers.update(
                        {"Authorization": f"Bearer {new_token}"}
                    )

                    logger.info(
                        f"Successfully refreshed OAuth token for user {self._email}"
                    )
                else:
                    logger.error(
                        f"Failed to refresh OAuth token for user {self._email}: No token returned"
                    )

        except Exception as e:
            logger.error(
                f"Error refreshing OAuth token for user {self._email}: {str(e)}"
            )
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
        self._refresh_timer = threading.Timer(
            self._auto_refresh_interval_seconds, self._refresh_oauth_token
        )
        self._refresh_timer.daemon = (
            True  # Allow program to exit even if timer is running
        )
        self._refresh_timer.start()

        interval_minutes = self._auto_refresh_interval_seconds / 60
        logger.debug(f"Scheduled next token refresh in {interval_minutes:.1f} minutes")

    #######################################
    def stop_auto_refresh(self) -> None:
        """
        Stops the automatic token refresh.

        This method can be called to manually stop the auto-refresh mechanism.
        """
        if (
            self._auto_refresh_enabled
            and hasattr(self, "_refresh_timer")
            and self._refresh_timer
        ):
            self._refresh_timer.cancel()
            self._auto_refresh_enabled = False
            logger.info(f"Auto-refresh stopped for user {self._email}")

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
            raise ValueError(
                "Manual token refresh is only available in auto-refresh mode"
            )

        try:
            old_token = self._oauth_token
            self._refresh_oauth_token()
            return self._oauth_token != old_token and self._oauth_token is not None
        except Exception as e:
            logger.error(f"Manual token refresh failed: {str(e)}")
            return False

    #######################################
    def get_token_info(self) -> dict:
        """
        Returns information about the current token and refresh configuration.

        Returns:
            dict: Dictionary containing token info and refresh settings.
        """
        return {
            "auto_refresh_enabled": self._auto_refresh_enabled,
            "email": self._email if self._auto_refresh_enabled else None,
            "refresh_interval_seconds": getattr(
                self, "_auto_refresh_interval_seconds", None
            ),
            "has_token": bool(self._oauth_token),
        }

    #######################################
    @staticmethod
    def get_userclient(
        user_email: str, 
        mip_api_key: str, 
        endpoint_base: Optional[str] = None
    ) -> "UserClient":
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

                UserClient._userclients_cache[user_email] = UserClient(
                    oauth_token=oauth_token, 
                    endpoint_base=endpoint_base
                )

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
    def __del__(self) -> None:
        """
        Cleanup method to stop auto-refresh when the object is destroyed.
        """
        if hasattr(self, "_auto_refresh_enabled") and self._auto_refresh_enabled:
            self.stop_auto_refresh()