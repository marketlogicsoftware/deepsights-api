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
This module contains the tests for the report retrieval functions.
"""

import pytest

from deepsights.utils import PollingTimeoutError
from tests.helpers.validation import (
    assert_valid_report_contentstore_sources,
    assert_valid_report_document_sources,
    assert_valid_report_result,
)


def _test_report_create_and_wait_briefly(user_client, test_data):
    """
    Test function to check the behavior of the report_wait_for_completion function.

    Very expensive, only run when necessary.
    """
    report_id = user_client.reports.create(test_data["question"])

    with pytest.raises(PollingTimeoutError):
        user_client.reports.wait_for_report(report_id, timeout=3)


def test_report_wait_for_completion(user_client, test_data):
    """
    Test function to check the behavior of the report_wait_for_completion function.
    """
    user_client.reports.wait_for_report(test_data["report_id"])


def test_report_get(user_client, test_data):
    """
    Test case for the report_get function.

    This test verifies that the report retrieved from the deepsights.report_get function
    has the expected attributes and properties.
    """
    report = user_client.reports.get(test_data["report_id"])

    assert report is not None
    assert report.id == test_data["report_id"]
    assert_valid_report_result(report)
    assert_valid_report_document_sources(report.document_sources)
    assert_valid_report_contentstore_sources(report.secondary_sources)
    assert_valid_report_contentstore_sources(report.news_sources)
