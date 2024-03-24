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
This module contains the functions to retrieve reports from the DeepSights self.
"""

from ratelimit import sleep_and_retry, limits
from deepsights.api import APIResource
from deepsights.deepsights.minions._minions import minion_wait_for_completion
from deepsights.deepsights.resources.reports._model import Report


#################################################
class ReportResource(APIResource):
    """
    Represents a resource for retrieving reports the DeepSights API.
    """

    #################################################
    @sleep_and_retry
    @limits(calls=3, period=60)
    def create(self, question: str) -> str:
        """
        Creates a new report by submitting a question to the DeepSights self.

        Args:

            question (str): The question to be submitted for the report.

        Returns:

            str: The ID of the created report's minion job.
        """

        body = {"input": question}
        response = self.api.post(
            "/minion-commander-service/desk-researches", body=body, timeout=5
        )

        return response["minion_job"]["id"]

    #################################################
    def wait_for_report(self, report_id: str, timeout=600):
        """
        Waits for the completion of a report.

        Args:

            report_id (str): The ID of the report.
            timeout (int, optional): The maximum time to wait for the report to complete, in seconds. Defaults to 600.

        Raises:

            ValueError: If the report fails to complete.
        """
        return minion_wait_for_completion(self.api, "desk-researches", report_id, timeout)

    #################################################
    def get(self, report_id: str) -> Report:
        """
        Loads a report from the DeepSights self.

        Args:

            report_id (str): The ID of the report to load.

        Returns:

            Report: The loaded report.
        """
        response = self.api.get(f"/minion-commander-service/desk-researches/{report_id}")

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
