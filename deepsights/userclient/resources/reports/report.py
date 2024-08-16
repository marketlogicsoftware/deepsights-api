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

import time
from ratelimit import sleep_and_retry, limits
from deepsights.api import APIResource
from deepsights.userclient.resources.reports._model import Report


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
            "/end-user-gateway-service/desk-researches", body=body, timeout=5
        )

        return response["desk_research"]["minion_job"]["id"]

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

            ValueError: If the report fails to complete.
        """
        # wait for completion
        start = time.time()
        while time.time() - start < timeout:
            response = self.api.get(
                f"end-user-gateway-service/desk-researches/{report_id}"
            )["desk_research"]["minion_job"]

            if response["status"] in ("CREATED", "STARTED"):
                time.sleep(2)
            elif response["status"].startswith("FAILED"):
                raise ValueError(
                    f"Report {report_id} failed to complete: {response['error_reason']}"
                )
            else:
                return self.get(report_id)

        raise ValueError(
            f"Report {report_id} failed to complete within {timeout} seconds."
        )

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

        if response["permission_validation_result"] == "RESTRICTED":
            return Report(
                **dict(
                    permission_validation=response["permission_validation_result"],
                    id=response["restricted_desk_research"]["desk_research_id"],
                    status="n/a",
                    question=response["restricted_desk_research"]["input"],
                    topic="n/a",
                    summary="n/a",
                    document_sources=[],
                    secondary_sources=[],
                    news_sources=[],
                )
            )
        else:
            return Report(
                **dict(
                    permission_validation=response["permission_validation_result"],
                    id=response["desk_research"]["minion_job"]["id"],
                    status=response["desk_research"]["minion_job"]["status"],
                    question=response["desk_research"]["context"]["input"],
                    topic=response["desk_research"]["context"]["topic"],
                    summary=response["desk_research"]["context"]["summary"],
                    document_sources=response["desk_research"]["context"][
                        "artifact_vector_search_results"
                    ] or [],
                    secondary_sources=response["desk_research"]["context"][
                        "scs_report_search_results"
                    ]
                    or [],
                    news_sources=response["desk_research"]["context"][
                        "scs_news_search_results"
                    ]
                    or [],
                )
            )
