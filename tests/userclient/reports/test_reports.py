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
This module contains the tests for the report retrieval functions.
"""

import os
import json
import pytest
import deepsights

# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_question = data["question"]
    test_report_id = data["report_id"]


# set up the API client
uc = deepsights.DeepSights().get_userclient(os.environ["MIP_IDENTITY_VALID_EMAIL"])


def _test_report_create_and_wait_briefly():
    """
    Test function to check the behavior of the report_wait_for_completion function.

    Very expensive, only run when necessary.
    """
    report_id = uc.reports.create(test_question)

    with pytest.raises(ValueError):
        uc.reports.wait_for_report(report_id, timeout=3)


def test_report_wait_for_completion():
    """
    Test function to check the behavior of the report_wait_for_completion function.
    """
    uc.reports.wait_for_report(test_report_id)


def test_report_get():
    """
    Test case for the report_get function.

    This test verifies that the report retrieved from the deepsights.report_get function
    has the expected attributes and properties.
    """
    report = uc.reports.get(test_report_id)

    assert report.id == test_report_id
    assert report.permission_validation in ("GRANTED", "GRANTED_WITH_DELETED_CONTENT")
    assert report.question is not None
    assert report.status == "COMPLETED"
    assert report.topic is not None
    assert report.summary is not None

    assert report.document_sources is not None
    assert len(report.document_sources) > 0
    for doc in report.document_sources:
        assert doc.id is not None
        assert doc.reference is not None
        assert doc.synopsis is not None
        assert doc.summary is not None
        assert doc.publication_date is not None

        assert len(doc.pages) > 0
        for page in doc.pages:
            assert page.id is not None
            assert page.page_number is not None

    for cs_results in (report.secondary_sources, report.news_sources):
        assert cs_results is not None
        assert len(cs_results) > 0
        for cs_result in cs_results:
            assert cs_result.id is not None
            
            if cs_result in report.secondary_sources or cs_result in report.news_sources:
                assert cs_result.reference is not None
            else:
                assert cs_result.reference is None

            assert cs_result.synopsis is None
            assert cs_result.summary is not None
            assert cs_result.text is None
            assert cs_result.source is not None
            assert cs_result.publication_date is not None

