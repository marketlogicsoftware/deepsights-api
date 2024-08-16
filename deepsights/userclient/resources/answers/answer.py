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
This module contains the functions to retrieve answers from the DeepSights API.
"""

import time
from deepsights.api import APIResource
from deepsights.userclient.resources.answers._model import (
    DocumentAnswerSet,
    DocumentAnswer,
)


#################################################
class AnswerResource(APIResource):
    """
    Represents a resource for retrieving answer sets from the DeepSights API.
    """

    _has_warned = False

    def _deprecation_warning(self):
        if not self._has_warned:
            self._has_warned = True
            print("\n=== DEPRECATION WARNING ===\nThe answers endpoint is deprecated, please use answersV2.\n\n")


    #################################################
    def create(self, question: str) -> str:
        """
        Creates a new answer set by submitting a question to the DeepSights API.

        Args:

            question (str): The question to be submitted for the answers.

        Returns:

            str: The ID of the created answer's minion job.
        """
        self._deprecation_warning()

        body = {"input": question}
        response = self.api.post(
            "end-user-gateway-service/answer-sets", body=body, timeout=5
        )

        return response["answer_set"]["minion_job"]["id"]

    #################################################
    def wait_for_answer(self, answer_set_id: str, timeout=30):
        """
        Waits for the completion of an answer set.

        Args:

            answer_set_id (str): The ID of the answer set.
            timeout (int, optional): The maximum time to wait for the answer set to complete, in seconds.
            Defaults to 30.

        Raises:

            ValueError: If the answer set fails to complete.
        """
        # wait for completion
        start = time.time()
        while time.time() - start < timeout:
            response = self.api.get(
                f"end-user-gateway-service/answer-sets/{answer_set_id}"
            )["answer_set"]["minion_job"]

            if response["status"] in ("CREATED", "STARTED"):
                time.sleep(2)
            elif response["status"].startswith("FAILED"):
                raise ValueError(
                    f"Answer set {answer_set_id} failed to complete: {response['error_reason']}"
                )
            else:
                return

        raise ValueError(
            f"Answer set {answer_set_id} failed to complete within {timeout} seconds."
        )

    #################################################
    def get(self, answer_set_id: str) -> DocumentAnswerSet:
        """
        Loads an answer set from the DeepSights API.

        Args:

            answer_set_id (str): The ID of the answer set to load.

        Returns:

            DocumentAnswerSet: The answer set.
        """
        self._deprecation_warning()

        response = self.api.get(f"end-user-gateway-service/answer-sets/{answer_set_id}")

        return DocumentAnswerSet(
            permission_validation=response["permission_validation_result"],
            answers=[
                DocumentAnswer.model_validate(answer)
                for answer in response["answer_set"]["context"][
                    "summarized_search_results"
                ]
            ],
            search_results=[
                DocumentAnswer.model_validate(answer)
                for answer in response["answer_set"]["context"]["search_results"]
            ],
        )

    #################################################
    def create_and_wait(self, question: str) -> DocumentAnswerSet:
        """
        Submits a question to the DeepSights API and waits for the answer set to complete.

        Args:

            api (API): An instance of the DeepSights API client.
            question (str): The question to be submitted for the answers.

        Returns:

            DocumentAnswerSet: The answer set.
        """
        answer_set_id = self.create(question)

        self.wait_for_answer(answer_set_id)

        return self.get(answer_set_id)
