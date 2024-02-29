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
This module contains the functions to retrieve reports from the DeepSights API.
"""

from ratelimit import sleep_and_retry, limits
from deepsights.api import DeepSights
from deepsights.minions._minions import minion_wait_for_completion
from deepsights.reports.model import Report


#################################################
@sleep_and_retry
@limits(calls=3, period=60)
def report_create(api: DeepSights, question: str) -> str:
    """
    Creates a new report by submitting a question to the DeepSights API.

    Args:

        api (DeepSights): An instance of the DeepSights API client.
        question (str): The question to be submitted for the report.

    Returns:

        str: The ID of the created report's minion job.
    """

    body = {"input": question}
    response = api.post(
        "/minion-commander-service/desk-researches", body=body, timeout=5
    )

    return response["minion_job"]["id"]


#################################################
def report_wait_for_completion(api: DeepSights, report_id: str, timeout=600):
    """
    Waits for the completion of a report.

    Args:

        api (DeepSights): The DeepSights API instance.
        report_id (str): The ID of the report.
        timeout (int, optional): The maximum time to wait for the report to complete, in seconds. Defaults to 600.

    Raises:

        ValueError: If the report fails to complete.
    """
    return minion_wait_for_completion(api, "desk-researches", report_id, timeout)


#################################################
def report_get(api: DeepSights, report_id: str) -> Report:
    """
    Loads a report from the DeepSights API.

    Args:

        api (DeepSights): An instance of the DeepSights API client.
        report_id (str): The ID of the report to load.

    Returns:

        Report: The loaded report.
    """
    response = api.get(f"/minion-commander-service/desk-researches/{report_id}")

    return Report(
        **dict(
            id=response["minion_job"]["id"],
            status=response["minion_job"]["status"],
            question=response["context"]["input"],
            language=response["context"]["input_language"],
            topic=response["context"]["topic"],
            summary=response["context"]["summary"],
            document_sources=response["context"]["artifact_vector_search_results"],
            news_sources=response["context"]["scs_news_search_results"],
        )
    )
