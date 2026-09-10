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
This module contains the tests for the user client text search functions.
"""

import pytest

from tests.helpers.validation import assert_valid_text_search_result

pytestmark = pytest.mark.integration


def test_text_search_finds_document_by_title(user_client):
    """
    Test that a lexical metadata search finds a known document by its own title.

    Lists one completed document from the corpus, then searches for its title and
    asserts the document is among the results.
    """
    _, documents = user_client.documents.list(page_size=1, status_filter=["COMPLETED"])
    if not documents or not documents[0].title:
        pytest.skip("no completed document with a title available in the test corpus")

    document = documents[0]
    results = user_client.documents.text_search(metadata_query=document.title, limit=25)

    assert len(results) > 0
    for result in results:
        assert_valid_text_search_result(result)
    assert document.id in [result.artifact.id for result in results]


def test_text_search_content_query(user_client, test_data):
    """
    Test the content query variant of text search.
    """
    results = user_client.documents.text_search(content_query=test_data["question"], limit=5)

    assert isinstance(results, list)
    assert len(results) <= 5
    for result in results:
        assert_valid_text_search_result(result)


def test_text_search_recency_sort(user_client, test_data):
    """
    Test that RECENCY sorting returns results ordered by publication date.
    """
    results = user_client.documents.text_search(
        content_query=test_data["question"],
        limit=10,
        sort_by="RECENCY",
    )

    dates = [result.artifact.publication_date for result in results if result.artifact.publication_date]
    assert dates == sorted(dates, reverse=True)


def test_text_search_validation_errors(user_client):
    """
    Test that text search properly validates input parameters.
    """
    with pytest.raises(ValueError, match="At least one of"):
        user_client.documents.text_search()

    with pytest.raises(ValueError, match="At least one of"):
        user_client.documents.text_search(metadata_query="   ")

    with pytest.raises(ValueError, match="512 characters or less"):
        user_client.documents.text_search(metadata_query="x" * 513)

    with pytest.raises(ValueError, match="Invalid metadata fields"):
        user_client.documents.text_search(metadata_query="q", metadata_fields=["not_a_field"])

    with pytest.raises(ValueError, match="between 1 and 100"):
        user_client.documents.text_search(metadata_query="q", limit=0)

    with pytest.raises(ValueError, match="sort_by"):
        user_client.documents.text_search(metadata_query="q", sort_by="SCORE")
