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


#################################################
def run_in_parallel(fun, args, max_workers=5):
    """
    Executes the given function in parallel using multiple threads.

    Args:

        fun (callable): The function to be executed in parallel.
        args (iterable): The arguments to be passed to the function.
        max_workers (int, optional): The maximum number of worker threads to use. Defaults to 5.

    Returns:
    
        list: A list of results returned by the function for each argument.
    """
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fun, arg) for arg in args]
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]

    return results
