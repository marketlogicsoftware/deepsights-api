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
This module contains base API client classes.
"""

import os
from typing import Dict

from ratelimit import limits, sleep_and_retry
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from deepsights.exceptions import AuthenticationError, RateLimitError


def _should_retry_http_error(exception: Exception) -> bool:
    """
    Determines if an HTTPError should be retried.

    Only retries server errors (5xx) and specific rate limiting errors.
    Client errors (4xx) like 404, 400, 401, 403 are not retried.

    Args:
        exception: The exception to check

    Returns:
        bool: True if the error should be retried, False otherwise
    """
    if isinstance(exception, HTTPError):
        if hasattr(exception, "response") and exception.response is not None:
            status_code = exception.response.status_code
            # Only retry server errors (5xx) and rate limiting (429)
            return status_code >= 500 or status_code == 429
        return False
    # Always retry connection and timeout errors
    return isinstance(exception, (ConnectionError, Timeout))


def _handle_http_error(response):
    """
    Handles HTTP errors and raises appropriate custom exceptions.

    Args:
        response: The HTTP response object

    Raises:
        AuthenticationError: If status code is 401 (Unauthorized)
        HTTPError: For other HTTP errors
    """
    if response.status_code == 401:
        raise AuthenticationError("Invalid API key or insufficient permissions")
    elif response.status_code in [429, 502, 503]:
        raise HTTPError(f"Retriable error {response.status_code}", response=response)
    else:
        response.raise_for_status()


def _handle_persistent_rate_limit(func):
    """
    Decorator to catch persistent 429 errors after retries and convert them to RateLimitError.

    This ensures consistent exception handling for both client-side and server-side rate limiting.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            if (
                hasattr(e, "response")
                and e.response is not None
                and e.response.status_code == 429
            ):
                raise RateLimitError(
                    "Server rate limit exceeded after retries. Please wait before making another request.",
                    retry_after=None,  # Server didn't provide retry-after info
                ) from e
            raise

    return wrapper


#################################################
class API:
    """
    Represents an API client.
    """

    #######################################
    def __init__(
        self,
        endpoint_base: str,
        pool_connections: int = 10,
        pool_maxsize: int = 20,
        default_timeout: int = 15,
    ) -> None:
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

        # setup adapters with connection pooling (no retries at session level)
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=0,  # Disable session-level retries, rely on application-level retry decorators
        )

        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        # set keep-alive headers
        self._session.headers.update(
            {"Connection": "keep-alive", "User-Agent": "deepsights-api/1.3.9"}
        )

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
    @_handle_persistent_rate_limit
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=_should_retry_http_error,
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
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: If the GET request fails with a non-200 status code and not in the expected_statuscodes list.
        """
        timeout = timeout or self._default_timeout
        response = self._session.get(
            self._endpoint(path), params=params, timeout=timeout
        )

        if (
            response.status_code not in [200, 201, 202]
            and response.status_code not in expected_statuscodes
        ):
            _handle_http_error(response)

        return response.json()

    #######################################
    @_handle_persistent_rate_limit
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=_should_retry_http_error,
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
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: If the GET request fails with a non-200 status code and not in the expected_statuscodes list.
        """
        timeout = timeout or self._default_timeout
        response = self._session.get(
            self._endpoint(path), params=params, timeout=timeout
        )

        if (
            response.status_code not in [200, 201, 202]
            and response.status_code not in expected_statuscodes
        ):
            _handle_http_error(response)

        return response.content

    #######################################
    @_handle_persistent_rate_limit
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=_should_retry_http_error,
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

        Raises:
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: For other HTTP errors.
        """
        timeout = timeout or self._default_timeout
        response = self._session.post(
            self._endpoint(path), params=params, json=body, timeout=timeout
        )

        if (
            response.status_code not in [200, 201, 202]
            and response.status_code not in expected_statuscodes
        ):
            _handle_http_error(response)

        return response.json()

    #######################################
    @_handle_persistent_rate_limit
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=_should_retry_http_error,
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

            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: If the DELETE request fails with a non-200 status code.
        """
        timeout = timeout or self._default_timeout
        response = self._session.delete(self._endpoint(path), timeout=timeout)

        if (
            response.status_code not in [200, 204]
            and response.status_code not in expected_statuscodes
        ):
            _handle_http_error(response)


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
