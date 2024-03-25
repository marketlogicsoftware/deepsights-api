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
This module contains base API client classes.
"""

import os
import logging
from typing import Dict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)
from requests import Session
from requests.exceptions import Timeout
from ratelimit import limits, sleep_and_retry


#################################################
class API:
    """
    Represents an API client.
    """

    #######################################
    def __init__(self, endpoint_base: str) -> None:
        """
        Initializes the API client.

        Args:

            endpoint_base (str): The base URL of the API endpoint.
        """

        # record endpoint base
        self._endpoint_base = endpoint_base
        if not self._endpoint_base.endswith("/"):
            self._endpoint_base += "/"

    #######################################
    def _endpoint(self, path: str) -> str:
        """
        Constructs the full endpoint URL by appending the given path to the base endpoint.

        Args:

            path (str): The path to be appended to the base endpoint.

        Returns:

            str: The full endpoint URL.
        """
        return self._endpoint_base + path.strip("/")

    #######################################
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=retry_if_exception_type(Timeout),
    )
    @sleep_and_retry
    @limits(calls=1000, period=60)
    def get(
        self, path: str, params: Dict = None, timeout=15, expected_statuscodes=[]
    ) -> Dict:
        """
        Sends a GET request to the specified path with optional parameters.

        Args:
            path (str): The path to send the GET request to.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.

        Returns:
            The JSON body of the server's response to the request.

        Raises:
            HTTPError: If the GET request fails with a non-200 status code and not in the expected_statuscodes list.
        """
        response = self._session.get(
            self._endpoint(path), params=params, timeout=timeout
        )

        if (
            response.status_code != 200
            and not response.status_code in expected_statuscodes
        ):
            logging.error(
                "GET %s failed with status code %s", path, response.status_code
            )
            response.raise_for_status()

        return response.json()

    #######################################
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=retry_if_exception_type(Timeout),
    )
    @sleep_and_retry
    @limits(calls=100, period=60)
    def post(
        self,
        path: str,
        body: Dict,
        params: Dict = None,
        timeout=15,
        expected_statuscodes=[],
    ) -> Dict:
        """
        Sends a POST request to the specified path with optional parameters.

        Args:
            path (str): The path to send the POST request to.
            body (Dict): The JSON body to include in the request.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.

        Returns:
            Dict: The JSON body of the server's response to the request.
        """
        response = self._session.post(
            self._endpoint(path), params=params, json=body, timeout=timeout
        )

        if (
            response.status_code != 200
            and not response.status_code in expected_statuscodes
        ):
            logging.error(
                "POST %s failed with status code %s", path, response.status_code
            )
            response.raise_for_status()

        return response.json()

    #######################################
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=retry_if_exception_type(Timeout),
    )
    @sleep_and_retry
    @limits(calls=1000, period=60)
    def delete(self, path: str, timeout=5):
        """
        Sends a DELETE request to the specified path.

        Args:

            path (str): The path to send the DELETE request to.
            timeout (int, optional): The timeout for the request in seconds. Defaults to 5.

        Raises:

            HTTPError: If the DELETE request fails with a non-200 status code.
        """
        response = self._session.delete(self._endpoint(path), timeout=timeout)

        if response.status_code != 200:
            logging.error(
                "DELETE %s failed with status code %s", path, response.status_code
            )
            response.raise_for_status()


#################################################
class APIKeyAPI(API):
    """
    Represents an API client using an api key for authentication.
    """

    #######################################
    def __init__(
        self, endpoint_base: str, api_key: str, api_key_env_var: str = None
    ) -> None:
        """
        Initializes the API client.

        Args:

            endpoint_base (str): The base URL of the API endpoint.
            api_key (str): The API key to be used for authentication.
            api_key_env_var (str, optional): The name of the environment variable that contains the API key.
                If not provided, the API key must be passed directly as an argument. Defaults to None.

        Raises:

            AssertionError: If neither API key nor environment variable is provided.
        """
        super().__init__(endpoint_base)

        # set api key
        assert (
            api_key or api_key_env_var
        ), "Must provide either API key or environment variable"
        if not api_key:
            api_key = os.environ.get(api_key_env_var)
        self._api_key = api_key

        # prepare session
        self._session = Session()
        self._session.headers.update({"X-Api-Key": self._api_key})


#################################################
class OAuthTokenAPI(API):
    """
    Represents an API client using an oauth token for authentication.
    """

    #######################################
    def __init__(self, endpoint_base: str, oauth_token: str) -> None:
        """
        Initializes the API client.

        Args:

            endpoint_base (str): The base URL of the API endpoint.
            oauth_token (str): The OAuth token to be used for authentication.
        """
        super().__init__(endpoint_base)

        # set token
        self._oauth_token = oauth_token

        # prepare session
        self._session = Session()
        self._session.headers.update({"Authorization": f"Bearer {self._oauth_token}"})
