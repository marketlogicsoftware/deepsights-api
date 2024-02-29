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

import json
import deepsights

# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_question = data["question"]


def test_answers_v1():
    """
    Test case for v1 of answer retrieval.
    """
    answers = deepsights.answers_get(deepsights.DeepSights(), test_question)

    assert len(answers) > 0
    for answer in answers:
        assert answer.id is not None
        assert answer.artifact_id is not None
        assert answer.artifact_type == "DOCUMENT"
        assert answer.artifact_description is not None
        assert answer.answer is not None
        assert answer.timestamp is not None
        assert answer.pages is not None
        assert len(answer.pages) > 0
        for page in answer.pages:
            assert page.id is not None
            assert page.page_number is not None


def test_answers_sync():
    """
    Test case for synchronous answer retrieval.

    Retrieves the answer set using the synchronous method `answer_set_get_sync` and performs various assertions on the returned answer set.
    """
    answer_set = deepsights.answer_set_get_sync(deepsights.DeepSights(), test_question)

    assert len(answer_set.answers) > 0
    for answer in answer_set.answers:
        assert answer.id is not None
        assert answer.artifact_id is not None
        assert answer.artifact_type == "DOCUMENT"
        assert answer.artifact_description is not None
        assert answer.answer is not None
        assert answer.timestamp is not None
        assert answer.pages is not None
        assert len(answer.pages) > 0
        for page in answer.pages:
            assert page.id is not None
            assert page.page_number is not None


def test_answers_async():
    """
    Test case for asynchronous answer retrieval.
    """
    minion_job_id = deepsights.answer_set_create(deepsights.DeepSights(), test_question)
    deepsights.answer_set_wait_for_completion(deepsights.DeepSights(), minion_job_id)
    answer_set = deepsights.answer_set_get(deepsights.DeepSights(), minion_job_id)

    assert len(answer_set.answers) > 0
    for answer in answer_set.answers:
        assert answer.id is not None
        assert answer.artifact_id is not None
        assert answer.artifact_type == "DOCUMENT"
        assert answer.artifact_description is not None
        assert answer.answer is not None
        assert answer.timestamp is not None
        assert answer.pages is not None
        assert len(answer.pages) > 0
        for page in answer.pages:
            assert page.id is not None
            assert page.page_number is not None
