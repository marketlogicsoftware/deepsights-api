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
This module contains the API client to authenticate against MIP users.
"""

import re
from typing import Optional

from requests.exceptions import HTTPError

from deepsights.api.api import APIKeyAPI


#################################################
class MIPIdentityResolver(APIKeyAPI):
    """
    This class provides the API client to authenticate against MIP users.
    """

    #######################################
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initializes the API client.

        Args:

            api_key (str, optional): The API key to be used for authentication. If not provided, it will be fetched from the environment variable MIP_API_KEY.
        """
        super().__init__(
            endpoint_base="https://apigee.mlsdevcloud.com/user-management-api/prod/v1",
            api_key=api_key,
            api_key_env_var="MIP_API_KEY",
        )

    #################################################
    def _check_email(self, email: str) -> None:
        """
        Check if the given email address is valid.

        Args:
            email (str): The email address to be checked.

        Raises:
            ValueError: If the email address is invalid.
        """
        # More robust email validation pattern
        pattern = (
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$"
        )
        if not email or not re.match(pattern, email):
            raise ValueError(f"Invalid email address: {email}")

    #################################################
    def get_oauth_token(self, email: str) -> Optional[str]:
        """
        Retrieves an OAuth token for impersonating a user.

        Args:
            email (str): Email address of the user to impersonate.

        Returns:
            Optional[str]: OAuth token if user exists, None otherwise.

        Raises:
            ValueError: If email format is invalid.
        """
        if not self._api_key:
            return None

        self._check_email(email)
        body = {"user_email": email}

        try:
            response = self.post(
                "user-service-adapter/deep-sights/oauth/_generate-user-token",
                body=body,
                timeout=5,
            )
        except HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

        return response["access_token"]
