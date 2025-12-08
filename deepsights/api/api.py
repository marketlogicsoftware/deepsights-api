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

import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, TypeVar

from ratelimit import limits, sleep_and_retry
from requests import Response, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, Timeout
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from deepsights._version import __version__ as _ds_version
from deepsights.exceptions import AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


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
    return isinstance(exception, (RequestsConnectionError, Timeout))


def _handle_http_error(response: Response) -> None:
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
    if response.status_code in [429, 502, 503]:
        raise HTTPError(f"Retriable error {response.status_code}", response=response)
    response.raise_for_status()


F = TypeVar("F", bound=Callable[..., Any])


def _handle_persistent_rate_limit(func: F) -> F:
    """
    Decorator to catch persistent 429 errors after retries and convert them to RateLimitError.

    This ensures consistent exception handling for both client-side and server-side rate limiting.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            if hasattr(e, "response") and e.response is not None and e.response.status_code == 429:
                logger.warning(
                    "Persistent 429 after retries in %s; converting to RateLimitError",
                    getattr(func, "__name__", "<wrapped>"),
                )
                raise RateLimitError(
                    "Server rate limit exceeded after retries. Please wait before making another request.",
                    retry_after=None,  # Server didn't provide retry-after info
                ) from e
            raise

    return wrapper  # type: ignore[return-value]


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
        default_timeout: int | None = None,
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
            {
                "Connection": "keep-alive",
                "User-Agent": f"deepsights-api/{_ds_version}",
            }
        )

        # store default timeout (env override if none provided)
        if default_timeout is None:
            env_timeout = os.environ.get("DEEPSIGHTS_HTTP_TIMEOUT")
            try:
                self._default_timeout = int(env_timeout) if env_timeout else 15
            except (TypeError, ValueError):
                self._default_timeout = 15
        else:
            self._default_timeout = default_timeout

    #######################################
    def close(self) -> None:
        """
        Close the underlying HTTP session.
        """
        try:
            self._session.close()
        except Exception:  # pylint: disable=broad-exception-caught
            # Best-effort close; ignore errors
            pass

    #######################################
    def __enter__(self) -> "API":
        return self

    #######################################
    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> Literal[False]:
        self.close()
        # Do not suppress exceptions
        return False

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
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Sends a GET request to the specified path with optional parameters.

        Args:
            path (str): The path to send the GET request to.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.
            headers (Dict[str, str], optional): Additional headers for this request only.

        Returns:
            The JSON body of the server's response to the request.

        Raises:
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: If the GET request fails with a non-200 status code and not in the expected_statuscodes list.
        """
        timeout = timeout or self._default_timeout
        expected_statuscodes = expected_statuscodes or []
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP GET %s params=%s timeout=%s", path, params, timeout)
        response = self._session.get(self._endpoint(path), params=params, timeout=timeout, headers=headers)  # type: ignore[call-arg]
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP GET %s -> %s", path, response.status_code)

        if response.status_code not in [200, 201, 202] and response.status_code not in expected_statuscodes:
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
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
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
            headers (Dict[str, str], optional): Additional headers for this request only.

        Returns:
            bytes: The raw content of the server's response.

        Raises:
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: If the GET request fails with a non-200 status code and not in the expected_statuscodes list.
        """
        timeout = timeout or self._default_timeout
        expected_statuscodes = expected_statuscodes or []
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP GET(content) %s params=%s timeout=%s", path, params, timeout)
        response = self._session.get(self._endpoint(path), params=params, timeout=timeout, headers=headers)  # type: ignore[call-arg]
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP GET(content) %s -> %s", path, response.status_code)

        if response.status_code not in [200, 201, 202] and response.status_code not in expected_statuscodes:
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
    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def post(
        self,
        path: str,
        body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Sends a POST request to the specified path with optional parameters.

        Args:
            path (str): The path to send the POST request to.
            body (Dict): The JSON body to include in the request.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.
            headers (Dict[str, str], optional): Additional headers for this request only.

        Returns:
            Dict: The JSON body of the server's response to the request.

        Raises:
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: For other HTTP errors.
        """
        timeout = timeout or self._default_timeout
        expected_statuscodes = expected_statuscodes or []
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP POST %s params=%s body=%s timeout=%s", path, params, body, timeout)
        response = self._session.post(self._endpoint(path), params=params, json=body, timeout=timeout, headers=headers)  # type: ignore[call-arg]
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP POST %s -> %s", path, response.status_code)

        if response.status_code not in [200, 201, 202] and response.status_code not in expected_statuscodes:
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
    @limits(calls=100, period=60)
    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def put(
        self,
        path: str,
        body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a PUT request to the specified path with optional parameters.

        Args:
            path (str): The path to send the PUT request to.
            body (Dict): The JSON body to include in the request.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.
            headers (Dict[str, str], optional): Additional headers for this request only.

        Returns:
            Optional[Dict]: The JSON body of the server's response, or None for 204 No Content.

        Raises:
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: For other HTTP errors.
        """
        timeout = timeout or self._default_timeout
        expected_statuscodes = expected_statuscodes or []
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP PUT %s params=%s body=%s timeout=%s", path, params, body, timeout)
        response = self._session.put(self._endpoint(path), params=params, json=body, timeout=timeout, headers=headers)  # type: ignore[attr-defined]
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP PUT %s -> %s", path, response.status_code)

        if response.status_code not in [200, 201, 204] and response.status_code not in expected_statuscodes:
            _handle_http_error(response)

        # Return None for 204 No Content or empty response body
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    #######################################
    @_handle_persistent_rate_limit
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(max=5),
        retry=_should_retry_http_error,
    )
    @sleep_and_retry
    @limits(calls=100, period=60)
    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def patch(
        self,
        path: str,
        body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a PATCH request to the specified path with optional parameters.

        Args:
            path (str): The path to send the PATCH request to.
            body (Dict): The JSON body to include in the request.
            params (Dict, optional): Optional parameters to include in the request. Defaults to None.
            timeout (int, optional): The timeout in seconds for the request. Defaults to 15.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.
            headers (Dict[str, str], optional): Additional headers for this request only.

        Returns:
            Optional[Dict]: The JSON body of the server's response, or None for 204 No Content.

        Raises:
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: For other HTTP errors.
        """
        timeout = timeout or self._default_timeout
        expected_statuscodes = expected_statuscodes or []
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP PATCH %s params=%s body=%s timeout=%s", path, params, body, timeout)
        response = self._session.patch(self._endpoint(path), params=params, json=body, timeout=timeout, headers=headers)  # type: ignore[attr-defined]
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP PATCH %s -> %s", path, response.status_code)

        if response.status_code not in [200, 201, 202, 204] and response.status_code not in expected_statuscodes:
            _handle_http_error(response)

        # Return None for 204 No Content or empty response body
        if response.status_code == 204 or not response.content:
            return None
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
    def delete(
        self,
        path: str,
        timeout: Optional[int] = None,
        expected_statuscodes: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Sends a DELETE request to the specified path.

        Args:
            path (str): The path to send the DELETE request to.
            timeout (int, optional): The timeout for the request in seconds. Defaults to 5.
            expected_statuscodes (List[int], optional): List of expected status codes. Defaults to an empty list.
            headers (Dict[str, str], optional): Additional headers for this request only.

        Raises:
            AuthenticationError: If the request fails with a 401 status code.
            RateLimitError: If the request fails with persistent 429 status code after retries.
            HTTPError: If the DELETE request fails with a non-200 status code.
        """
        timeout = timeout or self._default_timeout
        expected_statuscodes = expected_statuscodes or []
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP DELETE %s timeout=%s", path, timeout)
        response = self._session.delete(self._endpoint(path), timeout=timeout, headers=headers)  # type: ignore[call-arg]
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP DELETE %s -> %s", path, response.status_code)

        if response.status_code not in [200, 204] and response.status_code not in expected_statuscodes:
            _handle_http_error(response)


#################################################
class APIKeyAPI(API):
    """
    Represents an API client using an api key for authentication.
    """

    #######################################
    def __init__(
        self,
        endpoint_base: str,
        api_key: str | None,
        api_key_env_var: str | None = None,
        **kwargs: Any,
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
        assert api_key or api_key_env_var, "Must provide either API key or environment variable"
        api_key_value: str | None = api_key if api_key is not None else (os.environ.get(api_key_env_var) if api_key_env_var else None)
        # store for subclasses
        self._api_key: str | None = api_key_value

        # add api key to session headers if available
        if self._api_key is not None:
            self._session.headers.update({"X-Api-Key": self._api_key})


#################################################
class OAuthTokenAPI(API):
    """
    Represents an API client using an oauth token for authentication.
    """

    #######################################
    def __init__(self, endpoint_base: str, oauth_token: str, **kwargs: Any) -> None:
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
