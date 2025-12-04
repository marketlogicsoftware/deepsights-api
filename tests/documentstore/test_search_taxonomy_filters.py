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
Integration tests for search with taxonomy filters.
"""

import pytest

from deepsights.documentstore.resources.documents import TaxonomyFilter

pytestmark = pytest.mark.integration


# =========================================
# Search Taxonomy Filter Tests
# =========================================


def test_hybrid_search_with_taxonomy_filter(ds_client, test_data):
    """Test hybrid search with taxonomy filters."""
    # Use a non-existent taxonomy filter - should return filtered (likely empty) results
    taxonomy_filter = TaxonomyFilter(
        field="non-existent-taxonomy-id",
        values=["non-existent-taxon-id"],
    )

    results = ds_client.documentstore.documents.search(
        query=test_data["question"],
        taxonomy_filters=[taxonomy_filter],
    )

    # Should return empty or filtered results, not error
    assert isinstance(results, list)


def test_topic_search_with_taxonomy_filter(ds_client, test_data):
    """Test topic search with taxonomy filters."""
    taxonomy_filter = TaxonomyFilter(
        field="non-existent-taxonomy-id",
        values=["non-existent-taxon-id"],
    )

    results = ds_client.documentstore.documents.topic_search(
        query=test_data["question"],
        taxonomy_filters=[taxonomy_filter],
    )

    # Should return empty or filtered results, not error
    assert isinstance(results, list)


def test_hybrid_search_with_multiple_taxonomy_filters(ds_client, test_data):
    """Test hybrid search with multiple taxonomy filters."""
    taxonomy_filters = [
        TaxonomyFilter(field="taxonomy-1", values=["taxon-1", "taxon-2"]),
        TaxonomyFilter(field="taxonomy-2", values=["taxon-3"]),
    ]

    results = ds_client.documentstore.documents.search(
        query=test_data["question"],
        taxonomy_filters=taxonomy_filters,
    )

    # Should handle multiple filters without error
    assert isinstance(results, list)


def test_hybrid_search_result_has_taxonomy_field(ds_client, test_data):
    """Test that hybrid search results include custom_taxonomies field."""
    results = ds_client.documentstore.documents.search(query=test_data["question"])

    assert isinstance(results, list)
    if len(results) > 0:
        # All results should have custom_taxonomies attribute (may be empty list)
        for result in results:
            assert hasattr(result, "custom_taxonomies")
            assert isinstance(result.custom_taxonomies, list)


def test_topic_search_result_has_taxonomy_field(ds_client, test_data):
    """Test that topic search results include custom_taxonomies field."""
    results = ds_client.documentstore.documents.topic_search(query=test_data["question"])

    assert isinstance(results, list)
    if len(results) > 0:
        # All results should have custom_taxonomies attribute (may be empty list)
        for result in results:
            assert hasattr(result, "custom_taxonomies")
            assert isinstance(result.custom_taxonomies, list)


def test_hybrid_search_without_taxonomy_filter(ds_client, test_data):
    """Test that hybrid search still works without taxonomy filters."""
    results = ds_client.documentstore.documents.search(
        query=test_data["question"],
        taxonomy_filters=None,
    )

    assert isinstance(results, list)
    # Basic validation that search works
    for result in results:
        assert result.artifact_id is not None
        assert result.artifact_title is not None


def test_topic_search_without_taxonomy_filter(ds_client, test_data):
    """Test that topic search still works without taxonomy filters."""
    results = ds_client.documentstore.documents.topic_search(
        query=test_data["question"],
        taxonomy_filters=None,
    )

    assert isinstance(results, list)
    # Basic validation that search works
    for result in results:
        assert result.artifact_id is not None
        assert result.artifact_title is not None
