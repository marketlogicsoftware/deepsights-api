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
Integration tests for document taxonomy operations.
"""

import uuid

import pytest

pytestmark = pytest.mark.integration


# =========================================
# Document Taxonomy Tests
# =========================================


def test_document_get_taxonomies_validation(ds_client):
    """Test document taxonomy get validation for empty document_id."""
    with pytest.raises(AssertionError, match="Document ID is required"):
        ds_client.documentstore.documents.get_taxonomies("")


def test_document_set_taxonomy_validation(ds_client):
    """Test document taxonomy set validation for empty document_id."""
    with pytest.raises(AssertionError, match="Document ID is required"):
        ds_client.documentstore.documents.set_taxonomy(
            document_id="",
            taxonomy_id="test",
            taxon_ids=["test"],
        )


def test_document_update_taxonomies_validation(ds_client):
    """Test document taxonomy update validation."""
    from deepsights.documentstore.resources.documents import CustomTaxonomyUpdate

    # Empty document_id
    with pytest.raises(AssertionError, match="Document ID is required"):
        ds_client.documentstore.documents.update_taxonomies(
            document_id="",
            taxonomy_updates=[CustomTaxonomyUpdate(taxonomy_id="test")],
        )

    # Empty taxonomy_updates
    with pytest.raises(AssertionError, match="At least one taxonomy update is required"):
        ds_client.documentstore.documents.update_taxonomies(
            document_id="test-doc-id",
            taxonomy_updates=[],
        )


@pytest.mark.heavy
def test_document_taxonomy_lifecycle(ds_client):
    """Test full document taxonomy lifecycle: create taxonomy, upload doc, set taxons, verify, clear, delete."""
    # Create test taxonomy
    test_name = f"Test Doc Taxonomy {uuid.uuid4().hex[:8]}"
    taxonomy = ds_client.documentstore.taxonomies.create(
        name=test_name,
        external_id=f"test-doc-taxonomy-{uuid.uuid4().hex[:8]}",
    )

    try:
        # Create taxon type
        taxon_type = ds_client.documentstore.taxon_types.create(
            taxonomy_id=taxonomy.id,
            name=f"Test Type {uuid.uuid4().hex[:8]}",
        )

        # Create taxon
        taxon = ds_client.documentstore.taxons.create(
            taxonomy_id=taxonomy.id,
            taxon_type_id=taxon_type.id,
            name=f"Test Taxon {uuid.uuid4().hex[:8]}",
        )

        # Upload a test document
        artifact_id = ds_client.documentstore.documents.upload(
            "tests/data/test_presentation.pdf",
        )
        ds_client.documentstore.documents.wait_for_upload(artifact_id)

        try:
            # Set taxonomy on document
            ds_client.documentstore.documents.set_taxonomy(
                document_id=artifact_id,
                taxonomy_id=taxonomy.id,
                taxon_ids=[taxon.id],
            )

            # Get taxonomies from document
            taxonomies = ds_client.documentstore.documents.get_taxonomies(artifact_id)
            assert isinstance(taxonomies, list)

            # Find our taxonomy
            our_taxonomy = next((t for t in taxonomies if t.taxonomy_id == taxonomy.id), None)
            assert our_taxonomy is not None, f"Taxonomy {taxonomy.id} not found in document taxonomies"
            assert taxon.id in our_taxonomy.externally_provided, (
                f"Taxon {taxon.id} not in externally_provided: {our_taxonomy.externally_provided}"
            )

            # Clear taxonomy
            ds_client.documentstore.documents.clear_taxonomy(
                document_id=artifact_id,
                taxonomy_id=taxonomy.id,
            )

            # Verify cleared
            taxonomies = ds_client.documentstore.documents.get_taxonomies(artifact_id)
            our_taxonomy = next((t for t in taxonomies if t.taxonomy_id == taxonomy.id), None)
            if our_taxonomy:
                assert taxon.id not in our_taxonomy.externally_provided, f"Taxon {taxon.id} should be cleared from externally_provided"

        finally:
            # Delete document (best effort cleanup)
            try:
                ds_client.documentstore.documents.delete([artifact_id])
                ds_client.documentstore.documents.wait_for_delete(artifact_id, timeout=120)
            except Exception:
                pass  # Ignore cleanup failures

        # Cleanup taxon and taxon type
        ds_client.documentstore.taxons.delete(taxon.id)
        ds_client.documentstore.taxon_types.delete(taxon_type.id)

    finally:
        # Cleanup taxonomy
        ds_client.documentstore.taxonomies.delete(taxonomy.id)


@pytest.mark.heavy
def test_document_taxonomy_exclude(ds_client):
    """Test setting excluded taxon IDs on a document."""
    # Create test taxonomy
    test_name = f"Test Exclude Taxonomy {uuid.uuid4().hex[:8]}"
    taxonomy = ds_client.documentstore.taxonomies.create(
        name=test_name,
        external_id=f"test-exclude-taxonomy-{uuid.uuid4().hex[:8]}",
    )

    try:
        # Create taxon type and taxons
        taxon_type = ds_client.documentstore.taxon_types.create(
            taxonomy_id=taxonomy.id,
            name=f"Test Type {uuid.uuid4().hex[:8]}",
        )

        taxon_include = ds_client.documentstore.taxons.create(
            taxonomy_id=taxonomy.id,
            taxon_type_id=taxon_type.id,
            name=f"Include Taxon {uuid.uuid4().hex[:8]}",
        )

        taxon_exclude = ds_client.documentstore.taxons.create(
            taxonomy_id=taxonomy.id,
            taxon_type_id=taxon_type.id,
            name=f"Exclude Taxon {uuid.uuid4().hex[:8]}",
        )

        # Upload a test document
        artifact_id = ds_client.documentstore.documents.upload(
            "tests/data/test_presentation.pdf",
        )
        ds_client.documentstore.documents.wait_for_upload(artifact_id)

        try:
            # Set taxonomy with both included and excluded taxons
            ds_client.documentstore.documents.set_taxonomy(
                document_id=artifact_id,
                taxonomy_id=taxonomy.id,
                taxon_ids=[taxon_include.id],
                excluded_taxon_ids=[taxon_exclude.id],
            )

            # Get taxonomies from document
            taxonomies = ds_client.documentstore.documents.get_taxonomies(artifact_id)
            our_taxonomy = next((t for t in taxonomies if t.taxonomy_id == taxonomy.id), None)
            assert our_taxonomy is not None

            # Verify included and excluded
            assert taxon_include.id in our_taxonomy.externally_provided
            assert taxon_exclude.id in our_taxonomy.externally_excluded

        finally:
            # Delete document (best effort cleanup)
            try:
                ds_client.documentstore.documents.delete([artifact_id])
                ds_client.documentstore.documents.wait_for_delete(artifact_id, timeout=120)
            except Exception:
                pass  # Ignore cleanup failures

        # Cleanup
        ds_client.documentstore.taxons.delete(taxon_include.id)
        ds_client.documentstore.taxons.delete(taxon_exclude.id)
        ds_client.documentstore.taxon_types.delete(taxon_type.id)

    finally:
        ds_client.documentstore.taxonomies.delete(taxonomy.id)
