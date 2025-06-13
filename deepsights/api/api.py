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

import logging
import os
from typing import Dict

from ratelimit import limits, sleep_and_retry
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, ConnectionError, Timeout
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)
from urllib3.util.retry import Retry


#################################################
class API:
    """
    Represents an API client.
    """

    #######################################
    def __init__(self, endpoint_base: str, pool_connections: int = 10, pool_maxsize: int = 20, default_timeout: int = 15) -> None:
        """
        Initializes the API client.

        Args:

            endpoint_base (str): The base URL of the API endpoint.
            pool_connections (int): Number of connection pools to cache.
            pool_maxsize (int): Maximum number of connections to save in the pool.
            default_timeout (int): Default timeout for all requests in seconds.
        """

        # record endpoint base
        self._endpoint_base = endpoint_base
        if not self._endpoint_base.endswith("/"):
            self._endpoint_base += "/"
        
        # setup session with connection pooling
        self._session = Session()
        
        # configure retry strategy for connection-level retries
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "DELETE"]
        )
        
        # setup adapters with connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)
        
        # set keep-alive headers
        self._session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'deepsights-api/1.2.4'
        })
        
        # store default timeout
        self._default_timeout = default_timeout

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
        retry=retry_if_exception_type((Timeout, ConnectionError, HTTPError)),
    )
    @sleep_and_retry
    @limits(calls=1000, period=60)
    def get(
        self, path: str, params: Dict = None, timeout=None, expected_statuscodes=[]
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
        timeout = timeout or self._default_timeout
        logging.debug("GET %s with params: %s", self._endpoint(path), params)
        response = self._session.get(
            self._endpoint(path), params=params, timeout=timeout
        )
        logging.debug("GET %s returned status: %s", path, response.status_code)

        if (
            response.status_code not in [200, 201, 202]
            and response.status_code not in expected_statuscodes
        ):
            logging.error(
                "GET %s failed with status code %s: %s", path, response.status_code, response.text
            )
            if response.status_code in [429, 502, 503]:
                raise HTTPError(f"Retriable error {response.status_code}", response=response)
            response.raise_for_status()

        return response.json()

    #######################################
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=retry_if_exception_type((Timeout, ConnectionError, HTTPError)),
    )
    @sleep_and_retry
    @limits(calls=1000, period=60)
    def get_content(
        self, path: str, params: Dict = None, timeout=None, expected_statuscodes=[]
    ) -> bytes:
        """
        Sends a GET request to the specified path and returns the raw response content.

        This method is similar to get() but returns the raw response content instead of parsing it as JSON.
        Useful for downloading binary data like files or images.

        Args:
            path (str): The path to send the GET request to.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.

        Returns:
            bytes: The raw content of the server's response.

        Raises:
            HTTPError: If the GET request fails with a non-200 status code and not in the expected_statuscodes list.
        """
        timeout = timeout or self._default_timeout
        logging.debug("GET_CONTENT %s with params: %s", self._endpoint(path), params)
        response = self._session.get(
            self._endpoint(path), params=params, timeout=timeout
        )
        logging.debug("GET_CONTENT %s returned status: %s", path, response.status_code)

        if (
            response.status_code not in [200, 201, 202]
            and response.status_code not in expected_statuscodes
        ):
            logging.error(
                "GET_CONTENT %s failed with status code %s", path, response.status_code
            )
            if response.status_code in [429, 502, 503]:
                raise HTTPError(f"Retriable error {response.status_code}", response=response)
            response.raise_for_status()

        return response.content

    #######################################
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=retry_if_exception_type((Timeout, ConnectionError, HTTPError)),
    )
    @sleep_and_retry
    @limits(calls=100, period=60)
    def post(
        self,
        path: str,
        body: Dict,
        params: Dict = None,
        timeout=None,
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
        timeout = timeout or self._default_timeout
        logging.debug("POST %s with body: %s, params: %s", self._endpoint(path), body, params)
        response = self._session.post(
            self._endpoint(path), params=params, json=body, timeout=timeout
        )
        logging.debug("POST %s returned status: %s", path, response.status_code)

        if (
            response.status_code not in [200, 201, 202]
            and response.status_code not in expected_statuscodes
        ):
            logging.error(
                "POST %s failed with status code %s: %s", path, response.status_code, response.text
            )
            if response.status_code in [429, 502, 503]:
                raise HTTPError(f"Retriable error {response.status_code}", response=response)
            response.raise_for_status()

        return response.json()

    #######################################
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=retry_if_exception_type((Timeout, ConnectionError, HTTPError)),
    )
    @sleep_and_retry
    @limits(calls=1000, period=60)
    def delete(self, path: str, timeout=None, expected_statuscodes=[]):
        """
        Sends a DELETE request to the specified path.

        Args:

            path (str): The path to send the DELETE request to.
            timeout (int, optional): The timeout for the request in seconds. Defaults to 5.

        Raises:

            HTTPError: If the DELETE request fails with a non-200 status code.
        """
        timeout = timeout or self._default_timeout
        logging.debug("DELETE %s", self._endpoint(path))
        response = self._session.delete(self._endpoint(path), timeout=timeout)
        logging.debug("DELETE %s returned status: %s", path, response.status_code)

        if (
            response.status_code not in [200, 204]
            and response.status_code not in expected_statuscodes
        ):
            logging.error(
                "DELETE %s failed with status code %s: %s", path, response.status_code, response.text
            )
            if response.status_code in [429, 502, 503]:
                raise HTTPError(f"Retriable error {response.status_code}", response=response)
            response.raise_for_status()


#################################################
class APIKeyAPI(API):
    """
    Represents an API client using an api key for authentication.
    """

    #######################################
    def __init__(
        self, endpoint_base: str, api_key: str, api_key_env_var: str = None, **kwargs
    ) -> None:
        """
        Initializes the API client.

        Args:

            endpoint_base (str): The base URL of the API endpoint.
            api_key (str): The API key to be used for authentication.
            api_key_env_var (str, optional): The name of the environment variable that contains the API key.
                If not provided, the API key must be passed directly as an argument. Defaults to None.
            **kwargs: Additional arguments passed to the base API class.

        Raises:

            AssertionError: If neither API key nor environment variable is provided.
        """
        super().__init__(endpoint_base, **kwargs)

        # set api key
        assert api_key or api_key_env_var, (
            "Must provide either API key or environment variable"
        )
        if not api_key:
            api_key = os.environ.get(api_key_env_var)
        self._api_key = api_key

        # add api key to session headers
        self._session.headers.update({"X-Api-Key": self._api_key})


#################################################
class OAuthTokenAPI(API):
    """
    Represents an API client using an oauth token for authentication.
    """

    #######################################
    def __init__(self, endpoint_base: str, oauth_token: str, **kwargs) -> None:
        """
        Initializes the API client.

        Args:

            endpoint_base (str): The base URL of the API endpoint.
            oauth_token (str): The OAuth token to be used for authentication.
            **kwargs: Additional arguments passed to the base API class.
        """
        super().__init__(endpoint_base, **kwargs)

        # set token
        self._oauth_token = oauth_token

        # add oauth token to session headers
        self._session.headers.update({"Authorization": f"Bearer {self._oauth_token}"})
