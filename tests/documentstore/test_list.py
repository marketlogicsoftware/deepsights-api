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
Test the documents_list function
"""

import deepsights
import deepsights.documentstore.resources.documents._model


def test_document_list_basic(ds_client):
    """
    Test the basic documents list functionality for documentstore.

    This function tests the `documents.list` method by performing a basic list
    request and verifying the results structure.
    """
    number_of_results, documents = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        sort_order=deepsights.documentstore.resources.documents._model.SortingOrder.DESCENDING,
        sort_field=deepsights.documentstore.resources.documents._model.SortingField.CREATION_DATE,
        status_filter=["COMPLETED"],
    )

    assert number_of_results >= 0
    assert isinstance(documents, list)
    assert len(documents) <= 10

    for document in documents:
        assert document.id is not None
        assert document.title is not None or document.ai_generated_title is not None
        assert document.status is not None


def test_document_list_pagination(ds_client):
    """
    Test the documents list pagination functionality.

    This function tests different page sizes and page numbers to verify
    pagination works correctly.
    """
    # Test page size 5
    number_of_results_page1, documents_page1 = ds_client.documentstore.documents.list(
        page_size=5,
        page_number=0,
        sort_order=deepsights.documentstore.resources.documents._model.SortingOrder.DESCENDING,
        sort_field=deepsights.documentstore.resources.documents._model.SortingField.CREATION_DATE,
    )

    # Test page size 3
    number_of_results_page2, documents_page2 = ds_client.documentstore.documents.list(
        page_size=3,
        page_number=0,
        sort_order=deepsights.documentstore.resources.documents._model.SortingOrder.DESCENDING,
        sort_field=deepsights.documentstore.resources.documents._model.SortingField.CREATION_DATE,
    )

    # Both should return the same total count
    assert number_of_results_page1 == number_of_results_page2

    # Page 1 should have max 5 documents, page 2 should have max 3
    assert len(documents_page1) <= 5
    assert len(documents_page2) <= 3

    # If we have enough documents, first 3 should be the same
    if len(documents_page1) >= 3 and len(documents_page2) >= 3:
        for i in range(3):
            assert documents_page1[i].id == documents_page2[i].id


def test_document_list_sorting_by_title(ds_client):
    """
    Test the documents list sorting by title functionality.
    """
    # Test ascending order
    number_of_results_asc, documents_asc = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        sort_order=deepsights.documentstore.resources.documents._model.SortingOrder.ASCENDING,
        sort_field=deepsights.documentstore.resources.documents._model.SortingField.TITLE,
    )

    # Test descending order
    number_of_results_desc, documents_desc = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        sort_order=deepsights.documentstore.resources.documents._model.SortingOrder.DESCENDING,
        sort_field=deepsights.documentstore.resources.documents._model.SortingField.TITLE,
    )

    assert number_of_results_asc == number_of_results_desc
    assert len(documents_asc) == len(documents_desc)

    # If we have multiple documents, verify ordering is different
    if len(documents_asc) > 1 and len(documents_desc) > 1:
        # First document in ascending should be different from first in descending
        # (unless there's only one document or all have same title)
        asc_titles = [doc.title or doc.ai_generated_title for doc in documents_asc if doc.title or doc.ai_generated_title]
        desc_titles = [doc.title or doc.ai_generated_title for doc in documents_desc if doc.title or doc.ai_generated_title]

        if len(set(asc_titles)) > 1:  # More than one unique title
            assert asc_titles[0] != desc_titles[0] or len(asc_titles) == 1


def test_document_list_sorting_by_publication_date(ds_client):
    """
    Test the documents list sorting by publication date functionality.
    """
    number_of_results, documents = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        sort_order=deepsights.documentstore.resources.documents._model.SortingOrder.DESCENDING,
        sort_field=deepsights.documentstore.resources.documents._model.SortingField.PUBLICATION_DATE,
    )

    assert number_of_results >= 0
    assert isinstance(documents, list)

    # Verify documents with publication dates are sorted correctly
    docs_with_dates = [doc for doc in documents if doc.publication_date is not None]
    if len(docs_with_dates) > 1:
        for i in range(1, len(docs_with_dates)):
            assert docs_with_dates[i].publication_date <= docs_with_dates[i - 1].publication_date


def test_document_list_status_filter(ds_client):
    """
    Test the documents list status filtering functionality.
    """
    # Test with COMPLETED status filter
    number_of_results_completed, documents_completed = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        status_filter=["COMPLETED"],
    )

    # Test without status filter
    number_of_results_all, _ = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
    )

    # All documents in filtered result should have COMPLETED status
    for document in documents_completed:
        assert document.status == "COMPLETED"

    # Results with filter should be <= results without filter
    assert number_of_results_completed <= number_of_results_all


def test_document_list_multiple_status_filter(ds_client):
    """
    Test the documents list with multiple status filters.
    """
    number_of_results, documents = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        status_filter=["COMPLETED", "PROCESSING"],
    )

    assert number_of_results >= 0
    assert isinstance(documents, list)

    # All documents should have one of the allowed statuses
    allowed_statuses = {"COMPLETED", "PROCESSING"}
    for document in documents:
        assert document.status in allowed_statuses


def test_document_list_empty_status_filter(ds_client):
    """
    Test the documents list with empty status filter (should return all).
    """
    number_of_results, documents = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        status_filter=[],
    )

    assert number_of_results >= 0
    assert isinstance(documents, list)


def test_document_list_validation_errors(ds_client):
    """
    Test that documents_list properly validates input parameters.
    """
    import pytest

    # Test page size too large
    with pytest.raises(AssertionError, match="page size must be less than or equal to 100"):
        ds_client.documentstore.documents.list(page_size=101)

    # Test negative page number
    with pytest.raises(AssertionError, match="page number must be greater than 0"):
        ds_client.documentstore.documents.list(page_number=-1)

    # Test invalid sort order
    with pytest.raises(AssertionError, match="sort order must be"):
        ds_client.documentstore.documents.list(sort_order="INVALID")

    # Test invalid sort field
    with pytest.raises(AssertionError, match="sort field must be"):
        ds_client.documentstore.documents.list(sort_field="invalid_field")


# Keep the original test for backward compatibility
def test_document_list(ds_client):
    number_of_results, documents = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        sort_order=deepsights.documentstore.resources.documents._model.SortingOrder.DESCENDING,
        sort_field=deepsights.documentstore.resources.documents._model.SortingField.CREATION_DATE,
        status_filter=["COMPLETED"],
    )

    assert number_of_results >= 10
    assert len(documents) == 10

    for document in documents:
        assert document.id is not None
        assert document.title is not None or document.ai_generated_title is not None
        assert document.status is not None
