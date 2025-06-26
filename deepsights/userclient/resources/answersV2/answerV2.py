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
from deepsights.userclient.resources.answersV2._model import AnswerV2
from deepsights.utils import (
    PollingFailedError,
    PollingTimeoutError,
    poll_for_completion,
)


#################################################
class AnswerV2Resource(APIResource):
    """
    Represents a resource for retrieving answers V2 from the DeepSights API.
    """

    #################################################
    @limits(calls=10, period=60)
    def create(self, question: str) -> str:
        """
        Creates a new answer V2 by submitting a question to the DeepSights self.

        Args:

            question (str): The question to be submitted for the answer.

        Returns:

            str: The ID of the created answer's minion job.

        Raises:

            RateLimitError: If the rate limit of 10 calls per 60 seconds is exceeded.
        """
        try:
            body = {"input": question}
            response = self.api.post("/end-user-gateway-service/answers-v2", body=body)

            return response["answer_v2"]["minion_job"]["id"]
        except RateLimitException as e:
            raise RateLimitError(
                "Answer creation rate limit exceeded (10 calls per 60 seconds). Please wait before making another request.",
                retry_after=60,
            ) from e

    #################################################
    def wait_for_answer(self, answer_id: str, timeout=90) -> AnswerV2:
        """
        Waits for the completion of an answer.

        Args:

            answer_id (str): The ID of the answer.
            timeout (int, optional): The maximum time to wait for the answer to complete, in seconds. Defaults to 90.

        Returns:

                AnswerV2: The completed answer.

        Raises:

            PollingTimeoutError: If the answer fails to complete within timeout.
            PollingFailedError: If the answer fails to complete.
        """

        def get_status(resource_id: str):
            return self.api.get(f"end-user-gateway-service/answers-v2/{resource_id}")

        try:
            poll_for_completion(
                get_status_func=get_status,
                resource_id=answer_id,
                timeout=timeout,
                pending_statuses=["CREATED", "STARTED"],
                get_final_result_func=lambda rid: self.get(rid),
            )
            return self.get(answer_id)
        except PollingTimeoutError as e:
            raise PollingTimeoutError(
                f"Answer {answer_id} failed to complete within {timeout} seconds."
            ) from e
        except PollingFailedError as e:
            raise PollingFailedError(
                f"Answer {answer_id} failed to complete: {str(e)}"
            ) from e

    #################################################
    def get(self, answer_id: str) -> AnswerV2:
        """
        Loads an answer from the DeepSights self.

        Args:

            answer_id (str): The ID of the answer to load.

        Returns:

            AnswerV2: The loaded answer.
        """
        response = self.api.get(f"end-user-gateway-service/answers-v2/{answer_id}")

        if response.get("permission_validation_result") == "RESTRICTED":
            restricted_data = response.get("restricted_answer_v2", {})
            return AnswerV2(
                **dict(
                    permission_validation=response.get("permission_validation_result"),
                    id=restricted_data.get("answer_v2_id"),
                    status="n/a",
                    question=restricted_data.get("input"),
                    answer="n/a",
                    watchouts="n/a",
                    document_sources=[],
                    secondary_sources=[],
                    news_sources=[],
                    document_suggestions=[],
                    secondary_suggestions=[],
                    news_suggestions=[],
                )
            )
        else:
            answer_data = response.get("answer_v2", {})
            minion_job = answer_data.get("minion_job", {})
            context = answer_data.get("context", {})
            summary = context.get("summary", {})

            return AnswerV2(
                **dict(
                    permission_validation=response.get("permission_validation_result"),
                    id=minion_job.get("id"),
                    status=minion_job.get("status"),
                    question=context.get("input"),
                    answer=summary.get("answer"),
                    watchouts=summary.get("watchouts"),
                    document_sources=context.get("avs_results") or [],
                    secondary_sources=context.get("srs_results") or [],
                    news_sources=context.get("sns_results") or [],
                    document_suggestions=context.get("avs_suggestions") or [],
                    secondary_suggestions=context.get("srs_suggestions") or [],
                    news_suggestions=context.get("sns_suggestions") or [],
                )
            )

    #################################################
    @limits(calls=10, period=60)
    def create_and_wait(self, question: str, timeout=90) -> AnswerV2:
        """
        Submits a question to the DeepSights API and waits for the answer to complete.

        Args:

            question (str): The question to be submitted for the answers.
            timeout (int, optional): The maximum time to wait for the answer to complete, in seconds. Defaults to 90.

        Returns:

            AnswerV2: The answer.

        Raises:

            RateLimitError: If the rate limit of 10 calls per 60 seconds is exceeded.
            PollingTimeoutError: If the answer fails to complete within timeout.
            PollingFailedError: If the answer fails to complete.
        """
        try:
            return self.wait_for_answer(self.create(question), timeout=timeout)
        except RateLimitException as e:
            raise RateLimitError(
                "Answer creation rate limit exceeded (10 calls per 60 seconds). Please wait before making another request.",
                retry_after=60,
            ) from e
