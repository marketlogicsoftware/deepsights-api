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
This module contains threading utility functions used by the DeepSights API.
"""

import concurrent.futures
import logging
from typing import Any, Callable, Iterable, List


#################################################
def run_in_parallel(fun: Callable[[Any], Any], args: Iterable[Any], max_workers: int = 5) -> List[Any]:
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
        future_to_index = {executor.submit(fun, arg): i for i, arg in enumerate(args_list)}
        
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as exc:
                logging.error("Task %d failed with exception: %s", index, exc)
                raise exc

    return results
