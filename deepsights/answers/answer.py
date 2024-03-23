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

from deepsights.api import DeepSights
from deepsights.minions._minions import minion_wait_for_completion
from deepsights.answers.model import DocumentAnswerSet, DocumentAnswer


#################################################
def answerset_create(api: DeepSights, question: str) -> str:
    """
    Creates a new answer set by submitting a question to the DeepSights API.

    Args:

        api (DeepSights): An instance of the DeepSights API client.
        question (str): The question to be submitted for the answers.

    Returns:

        str: The ID of the created answer's minion job.
    """

    body = {"input": question}
    response = api.post("/minion-commander-service/answer-sets", body=body, timeout=5)

    return response["minion_job"]["id"]


#################################################
def answerset_wait_for_completion(api: DeepSights, answerset_id: str, timeout=30):
    """
    Waits for the completion of an answer set.

    Args:

        api (DeepSights): The DeepSights API instance.
        answerset_id (str): The ID of the answer set.
        timeout (int, optional): The maximum time to wait for the answer set to complete, in seconds.
        Defaults to 30.

    Raises:

        ValueError: If the answer set fails to complete.
    """
    return minion_wait_for_completion(api, "answer-sets", answerset_id, timeout)


#################################################
def answerset_get(api: DeepSights, answerset_id: str) -> DocumentAnswerSet:
    """
    Loads an answer set from the DeepSights API.

    Args:

        api (DeepSights): An instance of the DeepSights API client.
        answerset_id (str): The ID of the answer set to load.

    Returns:

        DocumentAnswerSet: The answer set.
    """
    response = api.get(f"/minion-commander-service/answer-sets/{answerset_id}")

    return DocumentAnswerSet(
        answers=[
            DocumentAnswer.model_validate(answer)
            for answer in response["context"]["summarized_search_results"]
        ]
    )


#################################################
def answerset_get_sync(api: DeepSights, question: str) -> DocumentAnswerSet:
    """
    Submits a question to the DeepSights API and waits for the answer set to complete.

    Args:

        api (DeepSights): An instance of the DeepSights API client.
        question (str): The question to be submitted for the answers.

    Returns:

        DocumentAnswerSet: The answer set.
    """
    answerset_id = answerset_create(api, question)

    answerset_wait_for_completion(api, answerset_id)

    return answerset_get(api, answerset_id)