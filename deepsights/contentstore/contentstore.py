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
This module contains the client to interact with the ContentStore API.
"""

import os
from typing import Callable, Optional

from deepsights.api.api import API, APIKeyAPI
from deepsights.api.unified_token import UnifiedTokenMixin
from deepsights.contentstore.resources import NewsResource, SecondaryResource

DEFAULT_ENDPOINT = "https://apigee.mlsdevcloud.com/secondary-content/api/"


#################################################
class ContentStore(UnifiedTokenMixin, APIKeyAPI):
    """
    This class provides the client to interact with the ContentStore API.

    Supports two authentication modes (mutually exclusive):
    1. API key authentication (existing mode)
    2. Unified token authentication with automatic refresh on 401
    """

    news: NewsResource
    secondary: SecondaryResource

    #######################################
    def __init__(
        self,
        api_key: str | None = None,
        endpoint_base: str | None = None,
        unified_token: str | None = None,
        refresh_callback: Optional[Callable[[], Optional[str]]] = None,
    ) -> None:
        """
        Initializes the API client.

        Args:
            api_key (str, optional): The API key to be used for authentication.
                If not provided, it will be fetched from the environment variable
                CONTENTSTORE_API_KEY. Mutually exclusive with unified_token.
            endpoint_base (str, optional): The base URL of the API endpoint.
                If not provided, the default endpoint base will be used.
            unified_token (str, optional): Bearer token for unified token authentication.
                Mutually exclusive with api_key.
            refresh_callback (Callable, optional): Callback function that returns a new
                token string, or None to signal permanent auth failure (stops retrying).
                Required when using unified_token. The callback MUST implement its own
                timeout to avoid blocking indefinitely.

        Raises:
            ValueError: If both api_key and unified_token are provided, or if neither
                is provided, or if unified_token is provided without refresh_callback.
        """
        endpoint = endpoint_base or DEFAULT_ENDPOINT

        # Determine which auth mode to use
        has_unified_token = unified_token is not None
        # Only check for API key if unified_token is not provided
        has_api_key = not has_unified_token and (api_key is not None or os.environ.get("CONTENTSTORE_API_KEY") is not None)

        # Validate mutual exclusivity (api_key parameter explicitly provided with unified_token)
        if api_key is not None and has_unified_token:
            raise ValueError("Cannot use both api_key and unified_token; choose one authentication method")
        if not has_api_key and not has_unified_token:
            raise ValueError("Must provide either api_key or unified_token for authentication")

        if has_unified_token:
            # Unified token mode
            if refresh_callback is None:
                raise ValueError("refresh_callback is required when using unified_token")

            # Initialize base API class directly (skip APIKeyAPI)
            API.__init__(self, endpoint_base=endpoint)
            # Initialize unified token mixin (assertions for mypy)
            assert unified_token is not None
            self.__init_unified_token__(unified_token, refresh_callback)
        else:
            # API key mode (existing behavior)
            super().__init__(
                endpoint_base=endpoint,
                api_key=api_key,
                api_key_env_var="CONTENTSTORE_API_KEY",
            )

        # Initialize resources (same for both modes)
        self.news = NewsResource(self)
        self.secondary = SecondaryResource(self)

    #######################################
    @classmethod
    def with_unified_token(
        cls,
        unified_token: str,
        refresh_callback: Callable[[], Optional[str]],
        endpoint_base: str | None = None,
    ) -> "ContentStore":
        """
        Alternative constructor for unified token authentication.

        Args:
            unified_token: Bearer token string for authentication.
            refresh_callback: Callback function that returns a new token on 401,
                or None to signal permanent failure (stops retrying). Must implement
                its own timeout to avoid blocking indefinitely.
            endpoint_base: Optional custom endpoint base URL.

        Returns:
            ContentStore instance configured with unified token authentication.
        """
        return cls(
            unified_token=unified_token,
            refresh_callback=refresh_callback,
            endpoint_base=endpoint_base,
        )
