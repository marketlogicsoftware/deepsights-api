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
This module contains the tests for the answer retrieval functions.
"""

import os
import json
import pytest
import deepsights

# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_question = data["question"]
    test_answerV2_id = data["answerV2_id"]


# set up the API client
uc = deepsights.DeepSights().get_userclient(os.environ["MIP_IDENTITY_VALID_EMAIL"])


# helper function to check the answer attributes
def _check_answer(answer):
    assert answer.question is not None
    assert answer.status == "COMPLETED"
    assert answer.permission_validation in ("GRANTED", "GRANTED_WITH_DELETED_CONTENT")
    assert answer.answer is not None
    assert answer.watchouts is not None

    for document_results in (answer.document_sources, answer.document_suggestions):
        assert document_results is not None
        for doc_result in document_results:
            assert doc_result.id is not None

            if doc_result in answer.document_sources:
                assert doc_result.reference is not None
            else:
                assert doc_result.reference is None

            assert doc_result.synopsis is not None
            assert doc_result.summary is None
            assert doc_result.text is None
            assert doc_result.publication_date is not None

            assert len(doc_result.pages) > 0
            for page in doc_result.pages:
                assert page.id is not None
                assert page.page_number is not None

    for cs_results in (
        answer.secondary_sources,
        answer.secondary_suggestions,
        answer.news_sources,
        answer.news_suggestions,
    ):
        assert cs_results is not None
        for cs_result in cs_results:
            assert cs_result.id is not None

            if (
                cs_result in answer.secondary_sources
                or cs_result in answer.news_sources
            ):
                assert cs_result.reference is not None
            else:
                assert cs_result.reference is None

            assert cs_result.synopsis is None
            assert cs_result.summary is None
            assert cs_result.text is not None
            assert cs_result.source is not None
            assert cs_result.publication_date is not None


def test_answerV2_create_and_wait():
    """
    Submit question and wait for answer.
    """
    answer = uc.answersV2.create_and_wait(test_question, timeout=90)

    _check_answer(answer)


def test_answerV2_create_and_wait_briefly():
    """
    Test function to check the behavior of the answer_wait_for_completion function.
    """
    answer_id = uc.answersV2.create(test_question)

    with pytest.raises(ValueError):
        uc.answersV2.wait_for_answer(answer_id, timeout=3)


def test_answerV2_wait_for_existing():
    """
    Test function to check the behavior of the answer_wait_for_completion function.
    """
    uc.answersV2.wait_for_answer(test_answerV2_id)


def test_answerV2_get():
    """
    Test case for the answer_get function.

    This test verifies that the answer retrieved from the deepsights.answer_get function
    has the expected attributes and properties.
    """
    answer = uc.answersV2.get(test_answerV2_id)

    _check_answer(answer)
