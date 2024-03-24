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
This module contains functions to interact with minions.
"""

import time
from deepsights.api import API


#################################################
def minion_wait_for_completion(
    api: API, minion_name: str, minion_job_id: str, timeout: int
):
    """
    Waits for the completion of a minion job.

    Args:

        api (API): The DeepSights API instance.
        minion_name (str): The name of the minion.
        minion_job_id (str): The ID of the answer set.
        timeout (int, optional): The maximum time to wait for the answer set to complete, in seconds.

    Raises:

        ValueError: If the answer set fails to complete.
    """
    # wait for completion
    start = time.time()
    while time.time() - start < timeout:
        response = api.get(f"/minion-commander-service/{minion_name}/{minion_job_id}")[
            "minion_job"
        ]

        if response["status"] in ("CREATED", "STARTED"):
            time.sleep(2)
        elif response["status"].startswith("FAILED"):
            raise ValueError(
                f"Minion {minion_job_id} failed to complete: {response['error_reason']}"
            )
        else:
            return

    raise ValueError(
        f"Minion {minion_job_id} failed to complete within {timeout} seconds."
    )
