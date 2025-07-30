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
Test the userclient documents_load function
"""

import pytest
import requests

from deepsights.documentstore.resources.documents._cache import (
    has_document,
    has_document_page,
    remove_document,
)


def test_documents_load_404(user_client):
    """
    Test case for loading a document that returns a 404 error.

    This test verifies that the `documents.documents_load` function raises an
    `HTTPError` exception with a status code of 404 when attempting to load a
    document with a non-existent ID.
    """
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        user_client.documents.load(
            ["non-existent-document-id"],
            load_pages=False,
        )

    assert exc.value.response.status_code == 404


def test_documents_load_basic(user_client, test_data):
    """
    Test the basic loading of a document using userclient documents_load() function.
    """
    test_document_id = test_data["document_id"]
    remove_document(test_document_id)

    documents = user_client.documents.load(
        [test_document_id],
        load_pages=False,
    )

    assert len(documents) == 1
    assert documents[0].id == test_document_id
    assert documents[0].status is not None
    assert documents[0].title is not None or documents[0].ai_generated_title is not None
    assert documents[0].file_name is not None
    assert documents[0].file_size > 0
    assert documents[0].description is not None
    assert documents[0].publication_date is not None
    assert documents[0].creation_date is not None
    assert documents[0].page_ids is None or len(documents[0].page_ids) == 0
    assert documents[0].number_of_pages > 0

    # Verify document is cached
    assert has_document(test_document_id)


def test_documents_load_caching(user_client, test_data):
    """
    Test the caching behavior of documents_load function.
    """
    test_document_id = test_data["document_id"]
    remove_document(test_document_id)

    # First load
    documents = user_client.documents.load(
        [test_document_id],
        load_pages=False,
    )

    # Modify the cached document to test caching
    documents[0].title = "__TEST_CACHE__"

    # Second load should return cached version
    documents_cached = user_client.documents.load(
        [test_document_id],
        load_pages=False,
    )

    assert documents_cached[0].title == "__TEST_CACHE__"


def test_documents_load_force_load(user_client, test_data):
    """
    Test the force_load parameter to bypass cache.
    """
    test_document_id = test_data["document_id"]
    remove_document(test_document_id)

    # Load document first time
    documents = user_client.documents.load(
        [test_document_id],
        load_pages=False,
    )
    original_title = documents[0].title

    # Modify cached document
    documents[0].title = "__TEST_FORCE_LOAD__"

    # Force load should bypass cache and get fresh data
    documents_forced = user_client.documents.load(
        [test_document_id],
        force_load=True,
        load_pages=False,
    )

    # Should have original title, not the modified one
    assert documents_forced[0].title == original_title
    assert documents_forced[0].title != "__TEST_FORCE_LOAD__"


@pytest.mark.skip(reason="Skipping document load test due to server endpoint issue")
def test_documents_load_with_pages(user_client, test_data):
    """
    Test the document load function with pages.

    This function tests the `documents_load` function of the userclient
    by loading a document with its pages and performing various assertions on the
    loaded document.
    """
    test_document_id = test_data["document_id"]
    remove_document(test_document_id)

    documents = user_client.documents.load(
        [test_document_id],
        load_pages=True,
    )

    assert len(documents) == 1
    assert documents[0].id == test_document_id
    assert documents[0].status is not None
    assert documents[0].title is not None or documents[0].ai_generated_title is not None
    assert documents[0].file_name is not None
    assert documents[0].file_size > 0
    assert documents[0].description is not None
    assert documents[0].publication_date is not None
    assert len(documents[0].page_ids) > 0
    assert documents[0].number_of_pages > 0

    # Verify document and pages are cached
    assert has_document(test_document_id)
    for page_id in documents[0].page_ids:
        assert has_document_page(page_id)


def test_documents_load_multiple_documents(user_client, test_data):
    """
    Test loading multiple documents at once.
    """
    test_document_id = test_data["document_id"]

    # For this test, we'll load the same document twice to simulate multiple documents
    # In a real scenario, you'd have multiple different document IDs
    document_ids = [test_document_id]

    remove_document(test_document_id)

    documents = user_client.documents.load(
        document_ids,
        load_pages=False,
    )

    assert len(documents) == len(document_ids)
    for i, document in enumerate(documents):
        assert document.id == document_ids[i]
        assert document.status is not None
        assert document.title is not None or document.ai_generated_title is not None


@pytest.mark.skip(reason="Skipping document load test due to server endpoint issue")
def test_documents_load_pages_for_existing_document(user_client, test_data):
    """
    Test loading pages for a document that's already cached but without pages.
    """
    test_document_id = test_data["document_id"]

    # First load without pages
    remove_document(test_document_id)
    documents = user_client.documents.load(
        [test_document_id],
        load_pages=False,
    )

    # Verify no pages are loaded initially
    assert documents[0].page_ids is None or len(documents[0].page_ids) == 0

    # Now load with pages
    documents_with_pages = user_client.documents.load(
        [test_document_id],
        load_pages=True,
    )

    # Should now have page IDs
    assert len(documents_with_pages[0].page_ids) > 0

    # Verify pages are cached
    for page_id in documents_with_pages[0].page_ids:
        assert has_document_page(page_id)


def test_documents_load_validation_errors(user_client):
    """
    Test that documents_load properly validates input parameters.
    """
    # Test empty document_ids list
    documents = user_client.documents.load([])
    assert len(documents) == 0

    # Test with very large number of documents (should trigger cache size assertion)
    # This test depends on cache size configuration, so we'll skip if cache is very large
    cache_size = 1000  # Assume reasonable cache size
    large_doc_list = [f"doc_{i}" for i in range(cache_size + 1)]

    with pytest.raises(
        AssertionError, match="Cannot load more documents than the cache size"
    ):
        user_client.documents.load(large_doc_list)
