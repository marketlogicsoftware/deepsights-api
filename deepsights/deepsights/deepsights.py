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
This module contains the DeepSights client.
"""

import os
from typing import Callable, Optional

from deepsights.api.api import APIKeyAPI
from deepsights.contentstore import ContentStore
from deepsights.deepsights.resources.quota import QuotaResource
from deepsights.documentstore import DocumentStore

ENDPOINT_BASE = "https://api.deepsights.ai/ds/v1"


#################################################
class DeepSights(APIKeyAPI):
    """
    This DeepSights client.

    The client can be initialized with API keys for DeepSights and/or ContentStore,
    or with unified token authentication for ContentStore.
    If authentication is not provided for a service, accessing that service will raise
    ValueError.
    """

    quota: QuotaResource
    _documentstore: Optional[DocumentStore]
    _contentstore: Optional[ContentStore]

    #######################################
    def __init__(
        self,
        ds_api_key: Optional[str] = None,
        cs_api_key: Optional[str] = None,
        ds_endpoint_base: Optional[str] = None,
        cs_endpoint_base: Optional[str] = None,
        cs_unified_token: Optional[str] = None,
        cs_refresh_callback: Optional[Callable[[], Optional[str]]] = None,
    ) -> None:
        """
        Initializes the DeepSights API client.

        Args:
            ds_api_key (str): The API key for the DeepSights API. If None, the DEEPSIGHTS_API_KEY environment variable is used.
            cs_api_key (str): The API key for the ContentStore API. If None, the CONTENTSTORE_API_KEY environment variable is used.
                Mutually exclusive with cs_unified_token.
            ds_endpoint_base (str, optional): The base URL of the DeepSights API endpoint.
                If not provided, the default endpoint base will be used.
            cs_endpoint_base (str, optional): The base URL of the ContentStore API endpoint.
                If not provided, the default endpoint base will be used.
            cs_unified_token (str, optional): Unified token for ContentStore authentication.
                Mutually exclusive with cs_api_key.
            cs_refresh_callback (Callable, optional): Callback for refreshing cs_unified_token.
                Required when using cs_unified_token.
        """
        super().__init__(
            endpoint_base=ds_endpoint_base or ENDPOINT_BASE,
            api_key=ds_api_key,
            api_key_env_var="DEEPSIGHTS_API_KEY",
        )

        self.quota = QuotaResource(self)

        # Only initialize documentstore if auth is available
        has_ds_key = ds_api_key is not None or os.environ.get("DEEPSIGHTS_API_KEY") is not None
        self._documentstore = DocumentStore(ds_api_key, ds_endpoint_base) if has_ds_key else None

        # Initialize contentstore based on auth mode
        has_cs_key = cs_api_key is not None or os.environ.get("CONTENTSTORE_API_KEY") is not None
        has_cs_unified = cs_unified_token is not None

        # Validate mutual exclusivity
        if has_cs_key and has_cs_unified:
            raise ValueError("Cannot use both cs_api_key and cs_unified_token; choose one authentication method")

        if has_cs_unified:
            self._contentstore = ContentStore(
                unified_token=cs_unified_token,
                refresh_callback=cs_refresh_callback,
                endpoint_base=cs_endpoint_base,
            )
        elif has_cs_key:
            self._contentstore = ContentStore(cs_api_key, cs_endpoint_base)
        else:
            self._contentstore = None

    @property
    def documentstore(self) -> DocumentStore:
        """
        Access the DocumentStore client.

        Raises:
            ValueError: If DeepSights API key was not configured.
        """
        if self._documentstore is None:
            raise ValueError("DocumentStore not configured. Provide ds_api_key or set DEEPSIGHTS_API_KEY environment variable.")
        return self._documentstore

    @property
    def contentstore(self) -> ContentStore:
        """
        Access the ContentStore client.

        Raises:
            ValueError: If ContentStore API key was not configured.
        """
        if self._contentstore is None:
            raise ValueError(
                "ContentStore not configured. Provide cs_api_key or set CONTENTSTORE_API_KEY "
                "environment variable, or provide cs_unified_token and cs_refresh_callback."
            )
        return self._contentstore
