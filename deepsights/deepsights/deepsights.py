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

from typing import Optional

from deepsights.api.api import APIKeyAPI
from deepsights.contentstore import ContentStore
from deepsights.deepsights.resources.quota import QuotaResource
from deepsights.documentstore import DocumentStore

ENDPOINT_BASE = "https://api.deepsights.ai/ds/v1"

#################################################
class DeepSights(APIKeyAPI):
    """
    This DeepSights client.
    """

    quota: QuotaResource
    documentstore: DocumentStore
    contentstore: ContentStore

    #######################################
    def __init__(
        self,
        ds_api_key: Optional[str] = None,
        cs_api_key: Optional[str] = None,
        endpoint_base: Optional[str] = None,
    ) -> None:
        """
        Initializes the DeepSights API client.

        Args:
            ds_api_key (str): The API key for the DeepSights API. If None, the DEEPSIGHTS_API_KEY environment variable is used.
            cs_api_key (str): The API key for the ContentStore API. If None, the CONTENTSTORE_API_KEY environment variable is used.
            endpoint_base (str, optional): The base URL of the API endpoint.
                If not provided, the default endpoint base will be used.
        """
        super().__init__(
            endpoint_base=endpoint_base or ENDPOINT_BASE,
            api_key=ds_api_key,
            api_key_env_var="DEEPSIGHTS_API_KEY",
        )

        self.quota = QuotaResource(self)
        self.documentstore = DocumentStore(ds_api_key)
        self.contentstore = ContentStore(cs_api_key)
