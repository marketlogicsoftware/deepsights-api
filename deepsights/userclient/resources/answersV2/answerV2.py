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
from deepsights.userclient.resources.answersV2._model import AnswerV2


#################################################
class AnswerV2Resource(APIResource):
    """
    Represents a resource for retrieving answers V2 from the DeepSights API.
    """

    #################################################
    @sleep_and_retry
    @limits(calls=3, period=60)
    def create(self, question: str) -> str:
        """
        Creates a new answer V2 by submitting a question to the DeepSights self.

        Args:

            question (str): The question to be submitted for the answer.

        Returns:

            str: The ID of the created answer's minion job.
        """

        body = {"input": question}
        response = self.api.post(
            "/end-user-gateway-service/answers-v2", body=body, timeout=5
        )

        return response["answer_v2"]["minion_job"]["id"]

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

            ValueError: If the answer fails to complete.
        """
        # wait for completion
        start = time.time()
        while time.time() - start < timeout:
            response = self.api.get(f"end-user-gateway-service/answers-v2/{answer_id}")[
                "answer_v2"
            ]["minion_job"]

            if response["status"] in ("CREATED", "STARTED"):
                time.sleep(2)
            elif response["status"].startswith("FAILED"):
                raise ValueError(
                    f"Answer {answer_id} failed to complete: {response['error_reason']}"
                )
            else:
                return self.get(answer_id)

        raise ValueError(
            f"Answer {answer_id} failed to complete within {timeout} seconds."
        )

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

        if response["permission_validation_result"] == "RESTRICTED":
            return AnswerV2(
                **dict(
                    permission_validation=response["permission_validation_result"],
                    id=response["restricted_answer_v2"]["answer_v2_id"],
                    status="n/a",
                    question=response["restricted_answer_v2"]["input"],
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
            return AnswerV2(
                **dict(
                    permission_validation=response["permission_validation_result"],
                    id=response["answer_v2"]["minion_job"]["id"],
                    status=response["answer_v2"]["minion_job"]["status"],
                    question=response["answer_v2"]["context"]["input"],
                    answer=response["answer_v2"]["context"]["summary"]["answer"],
                    watchouts=response["answer_v2"]["context"]["summary"]["watchouts"],
                    document_sources=response["answer_v2"]["context"]["avs_results"]
                    or [],
                    secondary_sources=response["answer_v2"]["context"]["srs_results"]
                    or [],
                    news_sources=response["answer_v2"]["context"]["sns_results"] or [],
                    document_suggestions=response["answer_v2"]["context"][
                        "avs_suggestions"
                    ]
                    or [],
                    secondary_suggestions=response["answer_v2"]["context"][
                        "srs_suggestions"
                    ]
                    or [],
                    news_suggestions=response["answer_v2"]["context"]["sns_suggestions"]
                    or [],
                )
            )
        
    #################################################
    def create_and_wait(self, question: str, timeout=60) -> AnswerV2:
        """
        Submits a question to the DeepSights API and waits for the answer to complete.

        Args:

            api (API): An instance of the DeepSights API client.
            question (str): The question to be submitted for the answers.
            timeout (int, optional): The maximum time to wait for the answer to complete, in seconds. Defaults to 60.

        Returns:

            AnswerV2: The answer.
        """
        return self.wait_for_answer(self.create(question), timeout=timeout)