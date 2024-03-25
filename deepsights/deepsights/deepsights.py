# Copyright 2024 Market Logic Software AG. All Rights Reserved.
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

from cachetools import TTLCache
from deepsights.api.api import APIKeyAPI
from deepsights.documentstore import DocumentStore
from deepsights.contentstore import ContentStore
from deepsights.userclient import UserClient
from deepsights.deepsights._mip_identity import MIPIdentityResolver
from deepsights.deepsights.resources.quota import QuotaResource


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
            ds_api_key: str = None,
            cs_api_key: str = None,
            mip_api_key: str = None,
        ) -> None:
            """
            Initializes the DeepSights API client.

            Args:
                ds_api_key (str): The API key for the DeepSights API. If None, the DEEPSIGHTS_API_KEY environment variable is used.
                cs_api_key (str): The API key for the ContentStore API. If None, the CONTENTSTORE_API_KEY environment variable is used.
                mip_api_key (str): The API key for the MIP API. If None, the MIP_API_KEY environment variable is used.
            """
            super().__init__(
                endpoint_base="https://api.deepsights.ai/ds/v1/",
                api_key=ds_api_key,
                api_key_env_var="DEEPSIGHTS_API_KEY",
            )

            self.quota = QuotaResource(self)
            self.documentstore = DocumentStore(ds_api_key)
            self.contentstore = ContentStore(cs_api_key)
            self._mip_identity_resolver = MIPIdentityResolver(mip_api_key)

            self.userclients = TTLCache(maxsize=100, ttl=240)

    #######################################
    def get_userclient(self, user_email: str) -> UserClient:
        """
        Retrieves a user client for the given user.

        Args:
            user_email (str): The email of the user to impersonate.

        Returns:
            UserClient: The user client for the given user. Will be cached.

        Raises:
            ValueError: If the user is not found.

        """
        # normalize the email
        user_email = user_email.lower().strip()

        # create the user client if it doesn't exist
        if user_email not in self.userclients:
            oauth_token = self._mip_identity_resolver.get_oauth_token(user_email)
            if not oauth_token:
                raise ValueError(f"User not found: {user_email}")

            self.userclients[user_email] = UserClient(oauth_token)

        return self.userclients[user_email]
