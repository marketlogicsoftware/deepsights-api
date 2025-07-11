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
Test the documents_search and document_pages_search functions
"""

import pytest

from tests.helpers.validation import (
    assert_descending_scores,
    assert_ranked_results,
    assert_valid_document_page_result,
    assert_valid_document_result,
    assert_valid_hybrid_search_result,
)


def test_document_pages_search_plain(ds_client, test_data):
    """
    Test the document pages search function with plain text.

    This function tests the `deepsights.document_pages_search` method by passing a `DeepSights` instance and a test embedding.
    It asserts that the search results are not empty and that each result has a document ID, an ID, and a score greater than 0.
    Additionally, it checks that the scores are sorted in descending order.
    """
    results = ds_client.documentstore.documents.search_pages(
        test_data["embedding"],
    )

    assert len(results) > 0
    for result in results:
        assert_valid_document_page_result(result)
    assert_descending_scores(results)


def test_document_pages_search_cutoff(ds_client, test_data):
    """
    Test case for the `document_pages_search` function with a high score cutoff.

    This test verifies that when the `document_pages_search` function is called with a high score cutoff (0.9999),
    it returns an empty list of results.
    """
    results = ds_client.documentstore.documents.search_pages(
        test_data["embedding"], min_score=0.9999
    )

    assert len(results) == 0


def test_document_pages_search_with_loading(ds_client, test_data):
    """
    Test the document pages search function with loading.

    This function tests the `deepsights.document_pages_search` function by performing a search
    with loading of pages. It asserts that the returned results meet certain criteria.
    """
    results = ds_client.documentstore.documents.search_pages(
        test_data["embedding"],
        max_results=10,
        load_pages=True,
    )

    assert len(results) == 10
    for result in results:
        assert_valid_document_page_result(result)
        assert result.text is not None
        assert result.page_number is not None
    assert_descending_scores(results)


def test_documents_search_plain(ds_client, test_data):
    """
    Test the search functionality for plain documents.

    This function tests the `deepsights.documents_search` method by passing a `deepsights.DeepSights` instance
    and a query embedding. It asserts that the search results are not empty and that each result has a valid ID,
    page matches, and score rank. It also asserts that the age rank is None and that the rank is equal to the
    score rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds_client.documentstore.documents.search_documents(
        query_embedding=test_data["embedding"],
    )

    assert len(results) > 0
    for result in results:
        assert_valid_document_result(result, expect_document=False)
    assert_ranked_results(results)


def test_documents_search_with_recency_low(ds_client, test_data):
    """
    Test the `documents_search` function with a low recency weight.

    This test verifies that the `documents_search` function returns the expected results
    when the recency weight is set to a low value, especially that the final rank is equal to the score rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds_client.documentstore.documents.search_documents(
        query_embedding=test_data["embedding"],
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for result in results:
        assert_valid_document_result(result)
        assert result.document is not None
    assert_ranked_results(results)


def test_documents_search_with_recency_high(ds_client, test_data):
    """
    Test the `documents_search` function with a high recency weight.

    This test verifies that the `documents_search` function returns the expected results
    when the recency weight is set to a high value, especially that the final rank is equal to the age rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds_client.documentstore.documents.search_documents(
        query_embedding=test_data["embedding"],
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for result in results:
        assert_valid_document_result(result)
        assert result.document is not None
    assert_ranked_results(results)


def test_documents_search_with_loading(ds_client, test_data):
    """
    Test the `documents_search` function with loading enabled.
    """
    results = ds_client.documentstore.documents.search_documents(
        query_embedding=test_data["embedding"],
        max_results=10,
        load_documents=True,
    )

    assert len(results) > 0
    for result in results:
        assert_valid_document_result(result)
        assert result.document is not None
        for page in result.page_matches:
            assert page.text is not None
    assert_ranked_results(results)


def test_hybrid_search_basic(ds_client, test_data):
    """
    Test the basic hybrid search functionality.

    This function tests the `hybrid_search` method by performing a basic search
    with a simple query and verifying the results structure.
    """
    results = ds_client.documentstore.documents.search(query=test_data["question"])

    assert isinstance(results, list)
    for result in results:
        assert_valid_hybrid_search_result(result)


def test_hybrid_search_extended(ds_client, test_data):
    """
    Test the hybrid search functionality with extended search enabled.

    This function tests the `hybrid_search` method with extended_search=True
    and verifies the results are properly structured.
    """
    results = ds_client.documentstore.documents.search(
        query=test_data["question"], extended_search=True
    )

    assert isinstance(results, list)
    for result in results:
        assert_valid_hybrid_search_result(result)
        assert result.artifact_title is not None
        assert len(result.artifact_title) > 0


def test_hybrid_search_validation_errors(ds_client):
    """
    Test that hybrid search properly validates input parameters.

    This function tests various invalid inputs to ensure proper error handling.
    """
    import pytest

    # Test None query
    with pytest.raises(ValueError, match="query.*required"):
        ds_client.documentstore.documents.search(query=None)

    # Test non-string query
    with pytest.raises(ValueError, match="query.*string"):
        ds_client.documentstore.documents.search(query=123)

    # Test empty query
    with pytest.raises(ValueError, match="query.*empty"):
        ds_client.documentstore.documents.search(query="   ")

    # Test query too long
    with pytest.raises(ValueError, match="query.*512 characters"):
        ds_client.documentstore.documents.search(query="x" * 601)
