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
This module contains the functions to retrieve answers v1 from the DeepSights API.
"""

import logging
from typing import List
from deepsights.api import DeepSights
from deepsights.answers.model import DocumentAnswer


#################################################
def answers_get(api: DeepSights, question: str, timeout=30) -> List[DocumentAnswer]:
    """
    Retrieves answers for a given question.

    This function is deprecated and will be removed in a future release. 
    Please use the answer_set_create, answer_set_wait_for_completion, 
    and answer_set_get functions instead.

    Args:

        api (DeepSights): The DeepSights API client.
        question (str): The question to retrieve answers for.
        timeout (int, optional): The timeout for the request. Defaults to 30.

    Returns:

        List[DocumentAnswer]: The list of answers for the question.
    """

    # deprecation warning
    logging.warning(
        "===== DEPRECATION WARNING =====\n"
        "The answers_get function is deprecated and will be removed in a future release. "
        "Please use the answer_set_create, answer_set_wait_for_completion, and answer_set_get functions instead."
    )

    body = {"search_term": question}
    response = api.post("/answer-service/answer-sets", body=body, timeout=timeout)

    return [DocumentAnswer.model_validate(answer) for answer in response["answers"]]
