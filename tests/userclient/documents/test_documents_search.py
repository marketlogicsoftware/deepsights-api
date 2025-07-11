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
This module contains the tests for the user client hybrid search functions.
"""

import pytest

from tests.helpers.validation import assert_valid_hybrid_search_result


def test_hybrid_search_basic(user_client, test_data):
    """
    Test the basic hybrid search functionality for user client.

    This function tests the `hybrid_search.search` method by performing a basic search
    with a simple query and verifying the results structure.
    """
    results = user_client.documents.search(query=test_data["question"])

    assert isinstance(results, list)
    for result in results:
        assert_valid_hybrid_search_result(result)
        assert result.artifact_title is not None
        assert len(result.artifact_title) > 0


def test_hybrid_search_extended(user_client, test_data):
    """
    Test the hybrid search functionality with extended search enabled.

    This function tests the `hybrid_search.search` method with extended_search=True
    and verifies the results are properly structured.
    """
    results = user_client.documents.search(
        query=test_data["question"], extended_search=True
    )

    assert isinstance(results, list)
    for result in results:
        assert_valid_hybrid_search_result(result)
        assert result.artifact_title is not None
        assert len(result.artifact_title) > 0


def test_hybrid_search_validation_errors(user_client):
    """
    Test that hybrid search properly validates input parameters.

    This function tests various invalid inputs to ensure proper error handling.
    """
    # Test non-string query
    with pytest.raises(ValueError, match="query.*string"):
        user_client.documents.search(query=123)

    # Test empty query
    with pytest.raises(ValueError, match="query.*empty"):
        user_client.documents.search(query="   ")

    # Test query too long
    with pytest.raises(ValueError, match="query.*512 characters"):
        user_client.documents.search(query="x" * 601)
