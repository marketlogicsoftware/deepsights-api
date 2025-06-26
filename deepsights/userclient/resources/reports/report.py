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
This module contains the functions to retrieve reports from the DeepSights self.
"""

from ratelimit import RateLimitException, limits

from deepsights.api import APIResource
from deepsights.exceptions import RateLimitError
from deepsights.userclient.resources.reports._model import Report
from deepsights.utils import (
    PollingFailedError,
    PollingTimeoutError,
    poll_for_completion,
)


#################################################
class ReportResource(APIResource):
    """
    Represents a resource for retrieving reports the DeepSights API.
    """

    #################################################
    @limits(calls=3, period=60)
    def create(self, question: str) -> str:
        """
        Creates a new report by submitting a question to the DeepSights self.

        Args:

            question (str): The question to be submitted for the report.

        Returns:

            str: The ID of the created report's minion job.

        Raises:

            RateLimitError: If the rate limit of 3 calls per 60 seconds is exceeded.
        """
        try:
            body = {"input": question}
            response = self.api.post(
                "/end-user-gateway-service/desk-researches", body=body
            )

            return response["desk_research"]["minion_job"]["id"]
        except RateLimitException as e:
            raise RateLimitError(
                "Report creation rate limit exceeded (3 calls per 60 seconds). Please wait before making another request.",
                retry_after=60,
            ) from e

    #################################################
    def wait_for_report(self, report_id: str, timeout=600) -> Report:
        """
        Waits for the completion of a report.

        Args:

            report_id (str): The ID of the report.
            timeout (int, optional): The maximum time to wait for the report to complete, in seconds. Defaults to 600.

        Returns:

            Report: The completed report.

        Raises:

            PollingTimeoutError: If the report fails to complete within timeout.
            PollingFailedError: If the report fails to complete.
        """

        def get_status(resource_id: str):
            return self.api.get(
                f"end-user-gateway-service/desk-researches/{resource_id}"
            )

        try:
            poll_for_completion(
                get_status_func=get_status,
                resource_id=report_id,
                timeout=timeout,
                pending_statuses=["CREATED", "STARTED"],
                get_final_result_func=lambda rid: self.get(rid),
            )
            return self.get(report_id)
        except PollingTimeoutError as e:
            raise PollingTimeoutError(
                f"Report {report_id} failed to complete within {timeout} seconds."
            ) from e
        except PollingFailedError as e:
            raise PollingFailedError(
                f"Report {report_id} failed to complete: {str(e)}"
            ) from e

    #################################################
    def get(self, report_id: str) -> Report:
        """
        Loads a report from the DeepSights self.

        Args:

            report_id (str): The ID of the report to load.

        Returns:

            Report: The loaded report.
        """
        response = self.api.get(f"end-user-gateway-service/desk-researches/{report_id}")

        if response.get("permission_validation_result") == "DELETED_CONTENT":
            return None
        elif response.get("permission_validation_result") == "RESTRICTED":
            restricted_data = response.get("restricted_desk_research", {})
            return Report(
                **dict(
                    permission_validation=response.get("permission_validation_result"),
                    id=restricted_data.get("desk_research_id"),
                    status="n/a",
                    question=restricted_data.get("input"),
                    topic="n/a",
                    summary="n/a",
                    document_sources=[],
                    secondary_sources=[],
                    news_sources=[],
                )
            )
        else:
            desk_research = response.get("desk_research", {})
            minion_job = desk_research.get("minion_job", {})
            context = desk_research.get("context", {})

            return Report(
                **dict(
                    permission_validation=response.get("permission_validation_result"),
                    id=minion_job.get("id"),
                    status=minion_job.get("status"),
                    question=context.get("input"),
                    topic=context.get("topic"),
                    summary=context.get("summary"),
                    document_sources=context.get("artifact_vector_search_results")
                    or [],
                    secondary_sources=context.get("scs_report_search_results") or [],
                    news_sources=context.get("scs_news_search_results") or [],
                )
            )
