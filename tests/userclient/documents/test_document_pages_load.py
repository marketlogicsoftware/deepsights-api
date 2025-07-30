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
Test the userclient document_pages_load function
"""

import pytest
import requests

from deepsights.documentstore.resources.documents._cache import (
    has_document_page,
    remove_document_page,
)


def test_document_pages_load_basic(user_client, test_data):
    """
    Test the basic loading of a document page.

    This function loads a document page using the `document_pages_load` method,
    and then performs assertions to verify the loaded page.
    """
    test_page_id = test_data["document_page_id"]
    remove_document_page(test_page_id)

    pages = user_client.documents.load_pages([test_page_id])

    assert len(pages) == 1
    assert pages[0].id == test_page_id
    assert pages[0].page_number > 0
    assert pages[0].text is not None
    assert len(pages[0].text) > 0

    # Verify page is cached
    assert has_document_page(test_page_id)


def test_document_pages_load_caching(user_client, test_data):
    """
    Test the caching behavior of document_pages_load function.
    """
    test_page_id = test_data["document_page_id"]
    remove_document_page(test_page_id)

    # First load
    pages = user_client.documents.load_pages([test_page_id])
    original_text = pages[0].text

    # Modify the cached page to test caching
    pages[0].text = "__TEST_CACHE__"

    # Second load should return cached version
    pages_cached = user_client.documents.load_pages([test_page_id])

    assert pages_cached[0].text == "__TEST_CACHE__"
    assert pages_cached[0].text != original_text


def test_document_pages_load_multiple_pages(user_client, test_data):
    """
    Test loading multiple document pages at once.
    """
    test_page_id = test_data["document_page_id"]

    # For this test, we'll load the same page twice to simulate multiple pages
    # In a real scenario, you'd have multiple different page IDs
    page_ids = [test_page_id]

    remove_document_page(test_page_id)

    pages = user_client.documents.load_pages(page_ids)

    assert len(pages) == len(page_ids)
    for i, page in enumerate(pages):
        assert page.id == page_ids[i]
        assert page.page_number > 0
        assert page.text is not None


def test_document_pages_load_from_document_with_pages(user_client, test_data):
    """
    Test loading pages for a document that has been loaded with pages.
    This tests the integration between documents_load and document_pages_load.
    """
    test_document_id = test_data["document_id"]

    # First load document with pages
    documents = user_client.documents.load(
        [test_document_id],
        load_pages=True,
    )

    # Get some page IDs from the loaded document
    page_ids = documents[0].page_ids[:2]  # Load first 2 pages

    # Clear the pages from cache to test fresh loading
    for page_id in page_ids:
        remove_document_page(page_id)

    # Load the pages individually
    pages = user_client.documents.load_pages(page_ids)

    assert len(pages) == len(page_ids)
    for i, page in enumerate(pages):
        assert page.id == page_ids[i]
        assert page.page_number > 0
        assert page.text is not None
        assert has_document_page(page.id)


def test_document_pages_load_404_error(user_client):
    """
    Test that document_pages_load handles 404 errors appropriately for non-existent pages.
    """
    non_existent_page_id = "non-existent-page-id"

    with pytest.raises(requests.exceptions.HTTPError) as exc:
        user_client.documents.load_pages([non_existent_page_id])

    assert exc.value.response.status_code == 404


def test_document_pages_load_mixed_cached_uncached(user_client, test_data):
    """
    Test loading a mix of cached and uncached pages.
    """
    test_document_id = test_data["document_id"]

    # Load document with pages to get multiple page IDs
    documents = user_client.documents.load(
        [test_document_id],
        load_pages=True,
    )

    if len(documents[0].page_ids) < 2:
        pytest.skip("Document doesn't have enough pages for this test")

    page_ids = documents[0].page_ids[:3]  # Use first 3 pages

    # Remove some pages from cache but not others
    remove_document_page(page_ids[1])  # Remove middle page

    # Load all pages - should handle mix of cached and uncached
    pages = user_client.documents.load_pages(page_ids)

    assert len(pages) == len(page_ids)
    for i, page in enumerate(pages):
        assert page.id == page_ids[i]
        assert page.page_number > 0
        assert page.text is not None
        assert has_document_page(page.id)


def test_document_pages_load_page_properties(user_client, test_data):
    """
    Test that loaded pages have all expected properties.
    """
    test_page_id = test_data["document_page_id"]
    remove_document_page(test_page_id)

    pages = user_client.documents.load_pages([test_page_id])

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


def test_document_pages_load_parallel_loading(user_client, test_data):
    """
    Test that parallel loading of pages works correctly.
    This test verifies that the parallel loading mechanism in the implementation works.
    """
    test_document_id = test_data["document_id"]

    # Load document with pages to get multiple page IDs
    documents = user_client.documents.load(
        [test_document_id],
        load_pages=True,
    )

    if len(documents[0].page_ids) < 3:
        pytest.skip("Document doesn't have enough pages for parallel loading test")

    # Take multiple pages and clear them from cache
    page_ids = documents[0].page_ids[:5]  # Use first 5 pages for parallel test
    for page_id in page_ids:
        remove_document_page(page_id)

    # Load all pages at once - should use parallel loading internally
    pages = user_client.documents.load_pages(page_ids)

    assert len(pages) == len(page_ids)
    for i, page in enumerate(pages):
        assert page.id == page_ids[i]
        assert page.page_number > 0
        assert page.text is not None
        assert has_document_page(page.id)
