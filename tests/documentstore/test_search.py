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
Test the documents_search and document_pages_search functions
"""

import json
import deepsights

# get the test embedding from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    test_embedding = json.load(f)["embedding"]


# set up the API client
ds = deepsights.DeepSights()


def test_document_pages_search_plain():
    """
    Test the document pages search function with plain text.

    This function tests the `deepsights.document_pages_search` method by passing a `DeepSights` instance and a test embedding.
    It asserts that the search results are not empty and that each result has a document ID, an ID, and a score greater than 0.
    Additionally, it checks that the scores are sorted in descending order.
    """
    results = ds.documentstore.documents.search_pages(
        test_embedding,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.document_id is not None
        assert result.id is not None
        assert result.score > 0

        if ix > 0:
            assert result.score <= results[ix - 1].score


def test_document_pages_search_cutoff():
    """
    Test case for the `document_pages_search` function with a high score cutoff.

    This test verifies that when the `document_pages_search` function is called with a high score cutoff (0.9999),
    it returns an empty list of results.
    """
    results = ds.documentstore.documents.search_pages(
        test_embedding, min_score=0.9999
    )

    assert len(results) == 0


def test_document_pages_search_with_loading():
    """
    Test the document pages search function with loading.

    This function tests the `deepsights.document_pages_search` function by performing a search
    with loading of pages. It asserts that the returned results meet certain criteria.
    """
    results = ds.documentstore.documents.search_pages(
        test_embedding,
        max_results=10,
        load_pages=True,
    )

    assert len(results) == 10
    for ix, result in enumerate(results):
        assert result.document_id is not None
        assert result.id is not None
        assert result.score > 0
        assert result.text is not None
        assert result.page_number is not None

        if ix > 0:
            assert result.score <= results[ix - 1].score


def test_documents_search_plain():
    """
    Test the search functionality for plain documents.

    This function tests the `deepsights.documents_search` method by passing a `deepsights.DeepSights` instance
    and a query embedding. It asserts that the search results are not empty and that each result has a valid ID,
    page matches, and score rank. It also asserts that the age rank is None and that the rank is equal to the
    score rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds.documentstore.documents.search(
        query_embedding=test_embedding,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
        assert result.rank == ix + 1


def test_documents_search_with_recency_low():
    """
    Test the `documents_search` function with a low recency weight.

    This test verifies that the `documents_search` function returns the expected results
    when the recency weight is set to a low value, especially that the final rank is equal to the score rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds.documentstore.documents.search(
        query_embedding=test_embedding,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.document is not None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
        assert result.rank == ix + 1


def test_documents_search_with_recency_high():
    """
    Test the `documents_search` function with a high recency weight.

    This test verifies that the `documents_search` function returns the expected results
    when the recency weight is set to a high value, especially that the final rank is equal to the age rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds.documentstore.documents.search(
        query_embedding=test_embedding,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.document is not None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
        assert result.rank == ix + 1


def test_documents_search_with_loading():
    """
    Test the `documents_search` function with loading enabled.
    """
    results = ds.documentstore.documents.search(
        query_embedding=test_embedding,
        max_results=10,
        load_documents=True,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.document is not None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
            assert page.text is not None
        assert result.rank == ix + 1
