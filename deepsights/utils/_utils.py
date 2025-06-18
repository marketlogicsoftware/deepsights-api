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
This module contains threading and polling utility functions used by the DeepSights API.
"""

import concurrent.futures
import logging
import time
from typing import Any, Callable, Dict, Iterable, List, Optional

import requests


#################################################
def run_in_parallel(
    fun: Callable[[Any], Any], args: Iterable[Any], max_workers: int = 5
) -> List[Any]:
    """
    Executes the given function in parallel using multiple threads, preserving input order.

    Args:

        fun (callable): The function to be executed in parallel.
        args (iterable): The arguments to be passed to the function.
        max_workers (int, optional): The maximum number of worker threads to use. Defaults to 5.

    Returns:

        list: A list of results returned by the function for each argument, in the same order as input.

    Raises:

        Exception: If any of the parallel tasks fail, the first exception encountered is raised.
    """
    args_list = list(args)
    results = [None] * len(args_list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(fun, arg): i for i, arg in enumerate(args_list)
        }

        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as exc:
                logging.error("Task %d failed with exception: %s", index, exc)
                raise exc

    return results


#################################################
class PollingTimeoutError(Exception):
    """Raised when polling operation times out."""

    pass


class PollingFailedError(Exception):
    """Raised when polling operation fails."""

    pass


#################################################
def poll_for_completion(
    get_status_func: Callable[[str], Dict[str, Any]],
    resource_id: str,
    timeout: int = 300,
    polling_interval: int = 2,
    pending_statuses: List[str] = None,
    failure_status_prefix: str = "FAILED",
    success_status: Optional[str] = None,
    get_final_result_func: Optional[Callable[[str], Any]] = None,
) -> Any:
    """
    Generic polling utility for waiting on asynchronous operations to complete.

    Args:
        get_status_func: Function that takes resource_id and returns status response dict
        resource_id: ID of the resource being polled
        timeout: Maximum time to wait in seconds
        polling_interval: Time between status checks in seconds
        pending_statuses: List of statuses that indicate operation is still in progress
        failure_status_prefix: Prefix indicating failure status
        success_status: Specific status indicating success (if None, any non-pending/non-failed is success)
        get_final_result_func: Optional function to get final result after success

    Returns:
        Final result from get_final_result_func if provided, otherwise status response

    Raises:
        PollingTimeoutError: If operation doesn't complete within timeout
        PollingFailedError: If operation fails
        requests.exceptions.HTTPError: If status check fails with 404 (for deletion scenarios)
    """
    if pending_statuses is None:
        pending_statuses = ["CREATED", "STARTED", "DELETING", "SCHEDULED_FOR_DELETING"]

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = get_status_func(resource_id)

            # Extract status from response (handle different response structures)
            status = None
            if isinstance(response, dict):
                # Try common status field locations
                status_dict = response
                if "minion_job" in response and "status" in response["minion_job"]:
                    status_dict = response["minion_job"]
                elif (
                    "desk_research" in response
                    and "minion_job" in response["desk_research"]
                ):
                    status_dict = response["desk_research"]["minion_job"]
                elif "answer_v2" in response and "minion_job" in response["answer_v2"]:
                    status_dict = response["answer_v2"]["minion_job"]

            status = status_dict.get("status")
            error_message = status_dict.get("error_message")

            if status is None:
                raise PollingFailedError(
                    f"Could not extract status from response for {resource_id}"
                )

            # Check if operation is still pending
            if status in pending_statuses:
                time.sleep(polling_interval)
                continue

            # Check if operation failed
            if status.startswith(failure_status_prefix):
                raise PollingFailedError(
                    f"Operation failed for resource {resource_id}: {error_message}"
                )

            # Check if we have a specific success status requirement
            if success_status is not None and status != success_status:
                time.sleep(polling_interval)
                continue

            # Operation completed successfully
            if get_final_result_func:
                return get_final_result_func(resource_id)
            else:
                return response

        except requests.exceptions.HTTPError as e:
            # Handle 404 for deletion scenarios
            if e.response.status_code == 404:
                raise e
            # Re-raise other HTTP errors
            raise e

    # Timeout reached
    elapsed_time = time.time() - start_time
    raise PollingTimeoutError(
        f"Operation for {resource_id} did not complete within {timeout} seconds (elapsed: {elapsed_time:.1f}s)"
    )
