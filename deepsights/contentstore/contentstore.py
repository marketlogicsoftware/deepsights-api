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

from deepsights.api.api import APIKeyAPI
from deepsights.contentstore.resources import NewsResource, SecondaryResource


#################################################
class ContentStore(APIKeyAPI):
    """
    This class provides the client to interact with the ContentStore API.
    """

    news: NewsResource
    secondary: SecondaryResource

    #######################################
    def __init__(self, api_key: str = None) -> None:
        """
        Initializes the API client.

        Args:

            api_key (str, optional): The API key to be used for authentication. If not provided, it will be fetched from the environment variable CONTENTSTORE_API_KEY.
        """
        super().__init__(
            endpoint_base="https://apigee.mlsdevcloud.com/secondary-content/api/",
            api_key=api_key,
            api_key_env_var="CONTENTSTORE_API_KEY",
        )

        self.news = NewsResource(self)
        self.secondary = SecondaryResource(self)
