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
This module contains the tests for the answer retrieval functions.
"""

import pytest

from deepsights.utils import PollingTimeoutError
from tests.helpers.validation import (
    assert_valid_answer_contentstore_sources,
    assert_valid_answer_contentstore_suggestions,
    assert_valid_answer_document_sources,
    assert_valid_answer_document_suggestions,
    assert_valid_answer_result,
)


def test_answerV2_create_and_wait(user_client, test_data):
    """
    Submit question and wait for answer.
    """
    answer = user_client.answersV2.create_and_wait(test_data["question"], timeout=90)

    assert_valid_answer_result(answer)
    assert_valid_answer_document_sources(answer.document_sources)
    assert_valid_answer_document_suggestions(answer.document_suggestions)
    assert_valid_answer_contentstore_sources(answer.secondary_sources)
    assert_valid_answer_contentstore_suggestions(answer.secondary_suggestions)
    assert_valid_answer_contentstore_sources(answer.news_sources)
    assert_valid_answer_contentstore_suggestions(answer.news_suggestions)


def test_answerV2_create_and_wait_briefly(user_client, test_data):
    """
    Test function to check the behavior of the answer_wait_for_completion function.
    """
    answer_id = user_client.answersV2.create(test_data["question"])

    with pytest.raises(PollingTimeoutError):
        user_client.answersV2.wait_for_answer(answer_id, timeout=3)


def test_answerV2_wait_for_existing(user_client, test_data):
    """
    Test function to check the behavior of the answer_wait_for_completion function.
    """
    user_client.answersV2.wait_for_answer(test_data["answerV2_id"])


def test_answerV2_get(user_client, test_data):
    """
    Test case for the answer_get function.

    This test verifies that the answer retrieved from the deepsights.answer_get function
    has the expected attributes and properties.
    """
    answer = user_client.answersV2.get(test_data["answerV2_id"])

    assert_valid_answer_result(answer)
    assert_valid_answer_document_sources(answer.document_sources)
    assert_valid_answer_document_suggestions(answer.document_suggestions)
    assert_valid_answer_contentstore_sources(answer.secondary_sources)
    assert_valid_answer_contentstore_suggestions(answer.secondary_suggestions)
    assert_valid_answer_contentstore_sources(answer.news_sources)
    assert_valid_answer_contentstore_suggestions(answer.news_suggestions)
