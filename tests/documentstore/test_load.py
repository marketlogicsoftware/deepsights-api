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
            ["aaa"],
            load_pages=False,
        )

    assert exc.value.response.status_code == 404


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


def test_document_load_with_pages(ds_client, test_data):
    """
    Test the document load function with pages.

    This function tests the `documents_load` function of the `deepsights` module
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
    assert documents[0].title is not None
    assert documents[0].file_name is not None
    assert documents[0].file_size > 0
    assert documents[0].description is not None
    assert documents[0].publication_date is not None
    assert len(documents[0].page_ids) > 0
    assert documents[0].number_of_pages > 0

    assert deepsights.documentstore.resources.documents._cache.has_document(
        test_document_id
    )
    for page_id in documents[0].page_ids:
        assert deepsights.documentstore.resources.documents._cache.has_document_page(
            page_id
        )


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
