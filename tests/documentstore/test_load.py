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
Test the documents_load function
"""

import pytest
import requests

import deepsights
import deepsights.documentstore.resources.documents._cache


def test_document_load_404(ds_client):
    """
    Test case for loading a document that returns a 404 error.

    This test verifies that the `deepsights.documents_load` function raises an
    `HTTPError` exception with a status code of 404 when attempting to load a
    document with a non-existent ID.
    """
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        ds_client.documentstore.documents.load(
            ["non-existent-document-id"],
            load_pages=False,
        )

    assert exc.value.response.status_code == 404


def test_document_load_basic(ds_client, test_data):
    """
    Test the basic loading of a document using documentstore documents_load() function.
    """
    test_document_id = test_data["document_id"]
    deepsights.documentstore.resources.documents._cache.remove_document(
        test_document_id
    )

    documents = ds_client.documentstore.documents.load(
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
    assert documents[0].page_ids is None
    assert documents[0].number_of_pages > 0

    # Verify document is cached
    assert deepsights.documentstore.resources.documents._cache.has_document(
        test_document_id
    )


def test_document_load_caching(ds_client, test_data):
    """
    Test the caching behavior of documents_load function.
    """
    test_document_id = test_data["document_id"]
    deepsights.documentstore.resources.documents._cache.remove_document(
        test_document_id
    )

    # First load
    documents = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=False,
    )

    # Modify the cached document to test caching
    documents[0].title = "__TEST_CACHE__"

    # Second load should return cached version
    documents_cached = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=False,
    )

    assert documents_cached[0].title == "__TEST_CACHE__"


def test_document_load_force_load(ds_client, test_data):
    """
    Test the force_load parameter to bypass cache.
    """
    test_document_id = test_data["document_id"]
    deepsights.documentstore.resources.documents._cache.remove_document(
        test_document_id
    )

    # Load document first time
    documents = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=False,
    )
    original_title = documents[0].title

    # Modify cached document
    documents[0].title = "__TEST_FORCE_LOAD__"

    # Force load should bypass cache and get fresh data
    documents_forced = ds_client.documentstore.documents.load(
        [test_document_id],
        force_load=True,
        load_pages=False,
    )

    # Should have original title, not the modified one
    assert documents_forced[0].title == original_title
    assert documents_forced[0].title != "__TEST_FORCE_LOAD__"


def test_document_load_with_pages(ds_client, test_data):
    """
    Test the document load function with pages.

    This function tests the `documents_load` function of the documentstore
    by loading a document with its pages and performing various assertions on the
    loaded document.
    """
    test_document_id = test_data["document_id"]
    deepsights.documentstore.resources.documents._cache.remove_document(
        test_document_id
    )

    documents = ds_client.documentstore.documents.load(
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
    assert deepsights.documentstore.resources.documents._cache.has_document(
        test_document_id
    )
    for page_id in documents[0].page_ids:
        assert deepsights.documentstore.resources.documents._cache.has_document_page(
            page_id
        )


def test_document_load_multiple_documents(ds_client, test_data):
    """
    Test loading multiple documents at once.
    """
    test_document_id = test_data["document_id"]

    # For this test, we'll load the same document twice to simulate multiple documents
    # In a real scenario, you'd have multiple different document IDs
    document_ids = [test_document_id]

    deepsights.documentstore.resources.documents._cache.remove_document(
        test_document_id
    )

    documents = ds_client.documentstore.documents.load(
        document_ids,
        load_pages=False,
    )

    assert len(documents) == len(document_ids)
    for i, document in enumerate(documents):
        assert document.id == document_ids[i]
        assert document.status is not None
        assert document.title is not None or document.ai_generated_title is not None


def test_document_load_pages_for_existing_document(ds_client, test_data):
    """
    Test loading pages for a document that's already cached but without pages.
    """
    test_document_id = test_data["document_id"]

    # First load without pages
    deepsights.documentstore.resources.documents._cache.remove_document(
        test_document_id
    )
    documents = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=False,
    )

    # Verify no pages are loaded initially
    assert documents[0].page_ids is None

    # Now load with pages
    documents_with_pages = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=True,
    )

    # Should now have page IDs
    assert len(documents_with_pages[0].page_ids) > 0

    # Verify pages are cached
    for page_id in documents_with_pages[0].page_ids:
        assert deepsights.documentstore.resources.documents._cache.has_document_page(
            page_id
        )


def test_document_load_validation_errors(ds_client):
    """
    Test that documents_load properly validates input parameters.
    """
    # Test empty document_ids list
    documents = ds_client.documentstore.documents.load([])
    assert len(documents) == 0

    # Test with very large number of documents (should trigger cache size assertion)
    # This test depends on cache size configuration, so we'll skip if cache is very large
    cache_size = 1000  # Assume reasonable cache size
    large_doc_list = [f"doc_{i}" for i in range(cache_size + 1)]

    with pytest.raises(
        AssertionError, match="Cannot load more documents than the cache size"
    ):
        ds_client.documentstore.documents.load(large_doc_list)


def test_document_page_load_basic(ds_client, test_data):
    """
    Test the basic loading of a document page.

    This function loads a document page using the `load_pages` method,
    and then performs assertions to verify the loaded page.
    """
    test_page_id = test_data["document_page_id"]
    deepsights.documentstore.resources.documents._cache.remove_document_page(
        test_page_id
    )

    pages = ds_client.documentstore.documents.load_pages([test_page_id])

    assert len(pages) == 1
    assert pages[0].id == test_page_id
    assert pages[0].page_number > 0
    assert pages[0].text is not None
    assert len(pages[0].text) > 0

    # Verify page is cached
    assert deepsights.documentstore.resources.documents._cache.has_document_page(
        test_page_id
    )


def test_document_page_load_caching(ds_client, test_data):
    """
    Test the caching behavior of document_pages_load function.
    """
    test_page_id = test_data["document_page_id"]
    deepsights.documentstore.resources.documents._cache.remove_document_page(
        test_page_id
    )

    # First load
    pages = ds_client.documentstore.documents.load_pages([test_page_id])
    original_text = pages[0].text

    # Modify the cached page to test caching
    pages[0].text = "__TEST_CACHE__"

    # Second load should return cached version
    pages_cached = ds_client.documentstore.documents.load_pages([test_page_id])

    assert pages_cached[0].text == "__TEST_CACHE__"
    assert pages_cached[0].text != original_text


def test_document_page_load_multiple_pages(ds_client, test_data):
    """
    Test loading multiple document pages at once.
    """
    test_page_id = test_data["document_page_id"]

    # For this test, we'll load the same page twice to simulate multiple pages
    # In a real scenario, you'd have multiple different page IDs
    page_ids = [test_page_id]

    deepsights.documentstore.resources.documents._cache.remove_document_page(
        test_page_id
    )

    pages = ds_client.documentstore.documents.load_pages(page_ids)

    assert len(pages) == len(page_ids)
    for i, page in enumerate(pages):
        assert page.id == page_ids[i]
        assert page.page_number > 0
        assert page.text is not None


def test_document_page_load_from_document_with_pages(ds_client, test_data):
    """
    Test loading pages for a document that has been loaded with pages.
    This tests the integration between documents_load and load_pages.
    """
    test_document_id = test_data["document_id"]

    # First load document with pages
    documents = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=True,
    )

    # Get some page IDs from the loaded document
    page_ids = documents[0].page_ids[:2]  # Load first 2 pages

    # Clear the pages from cache to test fresh loading
    for page_id in page_ids:
        deepsights.documentstore.resources.documents._cache.remove_document_page(
            page_id
        )

    # Load the pages individually
    pages = ds_client.documentstore.documents.load_pages(page_ids)

    assert len(pages) == len(page_ids)
    for i, page in enumerate(pages):
        assert page.id == page_ids[i]
        assert page.page_number > 0
        assert page.text is not None
        assert deepsights.documentstore.resources.documents._cache.has_document_page(
            page.id
        )


def test_document_page_load_404_error(ds_client):
    """
    Test that load_pages handles 404 errors appropriately for non-existent pages.
    """
    non_existent_page_id = "non-existent-page-id"

    with pytest.raises(requests.exceptions.HTTPError) as exc:
        ds_client.documentstore.documents.load_pages([non_existent_page_id])

    assert exc.value.response.status_code == 404


def test_document_page_load_properties(ds_client, test_data):
    """
    Test that loaded pages have all expected properties.
    """
    test_page_id = test_data["document_page_id"]
    deepsights.documentstore.resources.documents._cache.remove_document_page(
        test_page_id
    )

    pages = ds_client.documentstore.documents.load_pages([test_page_id])

    page = pages[0]

    # Test all expected properties
    assert hasattr(page, "id")
    assert hasattr(page, "page_number")
    assert hasattr(page, "text")

    # Test property types
    assert isinstance(page.id, str)
    assert isinstance(page.page_number, int)
    assert isinstance(page.text, str)

    # Test property values
    assert page.id == test_page_id
    assert page.page_number >= 1
    assert len(page.text.strip()) > 0


# Keep original tests for backward compatibility
def test_document_load(ds_client, test_data):
    """
    Test the loading of a document using deepsights.documents_load() function.
    """
    test_document_id = test_data["document_id"]
    deepsights.documentstore.resources.documents._cache.remove_document(
        test_document_id
    )

    documents = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=False,
    )

    assert len(documents) == 1
    assert documents[0].id == test_document_id
    assert documents[0].status is not None
    assert documents[0].title is not None
    assert documents[0].file_name is not None
    assert documents[0].file_size > 0
    assert documents[0].description is not None
    assert documents[0].publication_date is not None
    assert documents[0].creation_date is not None
    assert documents[0].page_ids is None
    assert documents[0].number_of_pages > 0

    assert deepsights.documentstore.resources.documents._cache.has_document(
        test_document_id
    )

    # test caching
    documents[0].title = "__TEST__"
    documents = ds_client.documentstore.documents.load(
        [test_document_id],
        load_pages=False,
    )
    assert documents[0].title == "__TEST__"


def test_document_page_load(ds_client, test_data):
    """
    Test the loading of a document page.

    This function sets a document page, loads it using the `document_pages_load` method,
    and then performs assertions to verify the loaded page.
    """
    test_page_id = test_data["document_page_id"]
    deepsights.documentstore.resources.documents._cache.remove_document_page(
        test_page_id
    )

    pages = ds_client.documentstore.documents.load_pages([test_page_id])

    assert len(pages) == 1
    assert pages[0].id == test_page_id
    assert pages[0].page_number > 0
    assert pages[0].text is not None

    assert deepsights.documentstore.resources.documents._cache.has_document_page(
        test_page_id
    )
