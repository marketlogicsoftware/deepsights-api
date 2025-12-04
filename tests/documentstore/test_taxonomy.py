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
Integration tests for custom taxonomy CRUD operations.
"""

import uuid

import pytest
import requests

# =========================================
# Taxonomy Tests
# =========================================


def test_taxonomy_search_basic(ds_client):
    """Test basic taxonomy search functionality."""
    total, taxonomies = ds_client.documentstore.taxonomies.search(page_size=10)

    assert total >= 0
    assert isinstance(taxonomies, list)
    assert len(taxonomies) <= 10

    for taxonomy in taxonomies:
        assert taxonomy.id is not None
        assert taxonomy.name is not None


def test_taxonomy_search_pagination(ds_client):
    """Test taxonomy search pagination."""
    total1, page1 = ds_client.documentstore.taxonomies.search(page_size=5, page_number=0)
    total2, page2 = ds_client.documentstore.taxonomies.search(page_size=5, page_number=1)

    # Total should be consistent across pages
    assert total1 == total2
    assert len(page1) <= 5
    assert len(page2) <= 5

    # Pages should not overlap (if enough data exists)
    if len(page1) == 5 and len(page2) > 0:
        page1_ids = {t.id for t in page1}
        page2_ids = {t.id for t in page2}
        assert page1_ids.isdisjoint(page2_ids)


def test_taxonomy_search_validation_errors(ds_client):
    """Test taxonomy search parameter validation."""
    with pytest.raises(AssertionError, match="Page size must be less than or equal to 100"):
        ds_client.documentstore.taxonomies.search(page_size=101)

    with pytest.raises(AssertionError, match="Page number must be greater than or equal to 0"):
        ds_client.documentstore.taxonomies.search(page_number=-1)


@pytest.mark.heavy
def test_taxonomy_crud_lifecycle(ds_client):
    """Test full taxonomy CRUD lifecycle: create, update, search, delete."""
    test_name = f"Test Taxonomy {uuid.uuid4().hex[:8]}"
    external_id = f"test-taxonomy-{uuid.uuid4().hex[:8]}"

    # Create
    taxonomy = ds_client.documentstore.taxonomies.create(
        name=test_name,
        external_id=external_id,
    )

    assert taxonomy.id is not None
    assert taxonomy.name == test_name
    assert taxonomy.external_id == external_id

    try:
        # Search by ID - should find our taxonomy
        total, results = ds_client.documentstore.taxonomies.search(ids=[taxonomy.id])
        assert total >= 1
        assert any(t.id == taxonomy.id for t in results)

        # Update
        updated_name = f"Updated {test_name}"
        ds_client.documentstore.taxonomies.update(
            taxonomy_id=taxonomy.id,
            name=updated_name,
        )

        # Verify update via search
        total, results = ds_client.documentstore.taxonomies.search(ids=[taxonomy.id])
        assert total >= 1
        updated = next((t for t in results if t.id == taxonomy.id), None)
        assert updated is not None
        assert updated.name == updated_name

    finally:
        # Cleanup - delete
        ds_client.documentstore.taxonomies.delete(taxonomy.id)

        # Verify deleted - search should not find it anymore
        total, results = ds_client.documentstore.taxonomies.search(ids=[taxonomy.id])
        assert not any(t.id == taxonomy.id for t in results)


def test_taxonomy_create_validation(ds_client):
    """Test that taxonomy creation validates required fields."""
    with pytest.raises(AssertionError, match="Taxonomy name is required"):
        ds_client.documentstore.taxonomies.create(name="")


def test_taxonomy_delete_not_found(ds_client):
    """Test that deleting non-existent taxonomy raises 404."""
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        ds_client.documentstore.taxonomies.delete("non-existent-id-12345")

    assert exc.value.response is not None
    assert exc.value.response.status_code in [404, 400]


# =========================================
# TaxonType Tests
# =========================================


@pytest.mark.heavy
def test_taxon_type_crud_lifecycle(ds_client):
    """Test full taxon type CRUD lifecycle."""
    test_name = f"Test Taxonomy for TaxonType {uuid.uuid4().hex[:8]}"

    # First create a taxonomy
    taxonomy = ds_client.documentstore.taxonomies.create(name=test_name)

    try:
        # Create taxon type
        taxon_type_name = f"Test Taxon Type {uuid.uuid4().hex[:8]}"
        taxon_type = ds_client.documentstore.taxon_types.create(
            taxonomy_id=taxonomy.id,
            name=taxon_type_name,
            description="A test taxon type for integration testing",
            external_id=f"test-taxon-type-{uuid.uuid4().hex[:8]}",
        )

        assert taxon_type.id is not None
        assert taxon_type.name == taxon_type_name
        assert taxon_type.description == "A test taxon type for integration testing"

        # Update taxon type
        updated_name = f"Updated {taxon_type_name}"
        ds_client.documentstore.taxon_types.update(
            taxon_type_id=taxon_type.id,
            name=updated_name,
            description="Updated description",
        )

        # Verify via taxonomy search (taxon types are included in taxonomy)
        total, results = ds_client.documentstore.taxonomies.search(ids=[taxonomy.id], include_taxons=True)
        assert total >= 1
        found_taxonomy = next((t for t in results if t.id == taxonomy.id), None)
        assert found_taxonomy is not None
        assert any(tt.id == taxon_type.id for tt in found_taxonomy.taxon_types)

        # Delete taxon type
        ds_client.documentstore.taxon_types.delete(taxon_type.id)

    finally:
        # Cleanup taxonomy
        ds_client.documentstore.taxonomies.delete(taxonomy.id)


def test_taxon_type_create_validation(ds_client):
    """Test that taxon type creation validates required fields."""
    with pytest.raises(AssertionError, match="Taxonomy ID is required"):
        ds_client.documentstore.taxon_types.create(taxonomy_id="", name="Test")

    with pytest.raises(AssertionError, match="Taxon type name is required"):
        ds_client.documentstore.taxon_types.create(taxonomy_id="some-id", name="")


# =========================================
# Taxon Tests
# =========================================


@pytest.mark.heavy
def test_taxon_crud_lifecycle(ds_client):
    """Test full taxon CRUD lifecycle."""
    test_name = f"Test Taxonomy for Taxon {uuid.uuid4().hex[:8]}"

    # Setup: Create taxonomy and taxon type
    taxonomy = ds_client.documentstore.taxonomies.create(name=test_name)

    try:
        taxon_type = ds_client.documentstore.taxon_types.create(
            taxonomy_id=taxonomy.id,
            name=f"Test Taxon Type {uuid.uuid4().hex[:8]}",
        )

        # Create taxon
        taxon_name = f"Test Taxon {uuid.uuid4().hex[:8]}"
        taxon = ds_client.documentstore.taxons.create(
            taxonomy_id=taxonomy.id,
            taxon_type_id=taxon_type.id,
            name=taxon_name,
            description="A test taxon",
            external_id=f"test-taxon-{uuid.uuid4().hex[:8]}",
        )

        assert taxon.id is not None
        assert taxon.name == taxon_name
        assert taxon.description == "A test taxon"
        assert taxon.taxon_type_id == taxon_type.id

        # Search for taxon
        total, results = ds_client.documentstore.taxons.search(ids=[taxon.id])
        assert total >= 1
        assert any(t.id == taxon.id for t in results)

        # Update taxon
        updated_name = f"Updated {taxon_name}"
        ds_client.documentstore.taxons.update(
            taxon_id=taxon.id,
            taxon_type_id=taxon_type.id,
            name=updated_name,
            description="Updated description",
        )

        # Verify update via search
        total, results = ds_client.documentstore.taxons.search(ids=[taxon.id])
        assert total >= 1
        updated = next((t for t in results if t.id == taxon.id), None)
        assert updated is not None
        assert updated.name == updated_name

        # Delete taxon
        ds_client.documentstore.taxons.delete(taxon.id)

        # Verify deleted
        total, results = ds_client.documentstore.taxons.search(ids=[taxon.id])
        assert not any(t.id == taxon.id for t in results)

        # Cleanup taxon type
        ds_client.documentstore.taxon_types.delete(taxon_type.id)

    finally:
        # Cleanup taxonomy
        ds_client.documentstore.taxonomies.delete(taxonomy.id)


@pytest.mark.heavy
def test_taxon_with_parent(ds_client):
    """Test creating taxon with parent relationships."""
    test_name = f"Test Taxonomy for Parent Taxon {uuid.uuid4().hex[:8]}"

    taxonomy = ds_client.documentstore.taxonomies.create(name=test_name)

    try:
        taxon_type = ds_client.documentstore.taxon_types.create(
            taxonomy_id=taxonomy.id,
            name=f"Hierarchical Type {uuid.uuid4().hex[:8]}",
        )

        # Create parent taxon
        parent = ds_client.documentstore.taxons.create(
            taxonomy_id=taxonomy.id,
            taxon_type_id=taxon_type.id,
            name=f"Parent Taxon {uuid.uuid4().hex[:8]}",
        )

        # Create child taxon with parent
        child = ds_client.documentstore.taxons.create(
            taxonomy_id=taxonomy.id,
            taxon_type_id=taxon_type.id,
            name=f"Child Taxon {uuid.uuid4().hex[:8]}",
            parent_ids=[parent.id],
        )

        assert child.parent_ids == [parent.id]

        # Cleanup in correct order (children first)
        ds_client.documentstore.taxons.delete(child.id)
        ds_client.documentstore.taxons.delete(parent.id)
        ds_client.documentstore.taxon_types.delete(taxon_type.id)

    finally:
        ds_client.documentstore.taxonomies.delete(taxonomy.id)


def test_taxon_search_basic(ds_client):
    """Test basic taxon search."""
    total, taxons = ds_client.documentstore.taxons.search(page_size=10)

    assert total >= 0
    assert isinstance(taxons, list)
    assert len(taxons) <= 10


def test_taxon_search_validation_errors(ds_client):
    """Test taxon search parameter validation."""
    with pytest.raises(AssertionError, match="Page size must be less than or equal to 100"):
        ds_client.documentstore.taxons.search(page_size=101)

    with pytest.raises(AssertionError, match="Page number must be greater than or equal to 0"):
        ds_client.documentstore.taxons.search(page_number=-1)


def test_taxon_create_validation(ds_client):
    """Test that taxon creation validates required fields."""
    with pytest.raises(AssertionError, match="Taxonomy ID is required"):
        ds_client.documentstore.taxons.create(taxonomy_id="", taxon_type_id="some-id", name="Test")

    with pytest.raises(AssertionError, match="Taxon type ID is required"):
        ds_client.documentstore.taxons.create(taxonomy_id="some-id", taxon_type_id="", name="Test")

    with pytest.raises(AssertionError, match="Taxon name is required"):
        ds_client.documentstore.taxons.create(taxonomy_id="some-id", taxon_type_id="some-id", name="")


# Mark all tests as integration tests
pytestmark = pytest.mark.integration
