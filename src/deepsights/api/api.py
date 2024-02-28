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
This module contains the base functions to interact with the DeepSights API.
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
    Represents an API client for interacting with the DeepSights APIs.
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

        # fall back to environment variable
        assert (
            api_key or api_key_env_var
        ), "Must provide either API key or environment variable"
        if not api_key:
            api_key = os.environ.get(api_key_env_var)
        self._api_key = api_key

        # record endpoint base
        self._endpoint_base = endpoint_base
        if not self._endpoint_base.endswith("/"):
            self._endpoint_base += "/"
        # prepare session
        self._session = Session()
        self._session.headers.update({"X-Api-Key": self._api_key})

    #######################################
    def _endpoint(self, path: str) -> str:
        """
        Constructs the full endpoint URL by appending the given path to the base endpoint.

        Args:

            path (str): The path to be appended to the base endpoint.

        Returns:

            str: The full endpoint URL.
        """
        return self._endpoint_base + path

    #######################################
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=retry_if_exception_type(Timeout),
    )
    @sleep_and_retry
    @limits(calls=1000, period=60)
    def get(self, path: str, params: Dict = None, timeout=15) -> Dict:
        """
        Sends a GET request to the specified path with optional parameters.

        Args:

            path (str): The path to send the GET request to.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.

        Returns:

            The JSON body of the server's response to the request.
        """

        response = self._session.get(
            self._endpoint(path), params=params, timeout=timeout
        )

        if response.status_code != 200:
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
    def post(self, path: str, body: Dict, params: Dict = None, timeout=15) -> Dict:
        """
        Sends a POST request to the specified path with optional parameters.

        Args:

            path (str): The path to send the POST request to.
            body (Dict): The JSON body to include in the request.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.

        Returns:

            Dict: The JSON body of the server's response to the request.
        """

        response = self._session.post(
            self._endpoint(path), params=params, json=body, timeout=timeout
        )

        if response.status_code != 200:
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
class ContentStore(API):
    """
    This class provides methods to interact with the ContentStore API.
    """

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


#################################################
class DeepSights(API):
    """
    This class provides methods to interact with the DeepSights API.
    """

    #######################################
    def __init__(self, api_key: str = None) -> None:
        """
        Initializes the API client.

        Args:
        
            api_key (str, optional): The API key to be used for authentication. If not provided, it will be fetched from the environment variable DEEPSIGHTS_API_KEY.
        """
        super().__init__(
            endpoint_base="https://api.deepsights.ai/ds/v1/",
            api_key=api_key,
            api_key_env_var="DEEPSIGHTS_API_KEY",
        )
