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
This module contains functions for managing document taxonomy assignments.
"""

from typing import List, Optional

from deepsights.api import APIResource
from deepsights.documentstore.resources.documents._model import (
    CustomTaxonomyUpdate,
    DocumentTaxonomyData,
)


#################################################
def document_get_taxonomies(
    resource: APIResource,
    document_id: str,
) -> List[DocumentTaxonomyData]:
    """
    Get taxonomy assignments for a document.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        document_id (str): The ID of the document.

    Returns:
        List[DocumentTaxonomyData]: List of taxonomy data assigned to the document.
    """
    assert document_id, "Document ID is required."

    response = resource.api.get(f"/artifact-service/artifacts/{document_id}")

    taxonomies_data = response.get("custom_taxonomies_data") or []
    return [DocumentTaxonomyData.model_validate(t) for t in taxonomies_data]


#################################################
def document_update_taxonomies(
    resource: APIResource,
    document_id: str,
    taxonomy_updates: List[CustomTaxonomyUpdate],
) -> None:
    """
    Update taxonomy assignments for a document.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        document_id (str): The ID of the document.
        taxonomy_updates (List[CustomTaxonomyUpdate]): List of taxonomy updates to apply.

    Returns:
        None
    """
    assert document_id, "Document ID is required."
    assert taxonomy_updates, "At least one taxonomy update is required."

    body = {
        "custom_taxonomies": [
            {
                "taxonomy_id": update.taxonomy_id,
                "provided_taxon_ids": update.provided_taxon_ids,
                "excluded_taxon_ids": update.excluded_taxon_ids,
            }
            for update in taxonomy_updates
        ]
    }

    resource.api.patch(f"/artifact-service/artifacts/{document_id}/metadata", body=body)


#################################################
def document_set_taxonomy(
    resource: APIResource,
    document_id: str,
    taxonomy_id: str,
    taxon_ids: List[str],
    excluded_taxon_ids: Optional[List[str]] = None,
) -> None:
    """
    Convenience function to set taxonomy assignments for a single taxonomy on a document.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        document_id (str): The ID of the document.
        taxonomy_id (str): The ID of the taxonomy.
        taxon_ids (List[str]): List of taxon IDs to assign.
        excluded_taxon_ids (List[str], optional): List of taxon IDs to exclude.

    Returns:
        None
    """
    update = CustomTaxonomyUpdate(
        taxonomy_id=taxonomy_id,
        provided_taxon_ids=taxon_ids,
        excluded_taxon_ids=excluded_taxon_ids or [],
    )
    document_update_taxonomies(resource, document_id, [update])


#################################################
def document_clear_taxonomy(
    resource: APIResource,
    document_id: str,
    taxonomy_id: str,
) -> None:
    """
    Clear all taxonomy assignments for a specific taxonomy on a document.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        document_id (str): The ID of the document.
        taxonomy_id (str): The ID of the taxonomy to clear.

    Returns:
        None
    """
    document_set_taxonomy(resource, document_id, taxonomy_id, taxon_ids=[], excluded_taxon_ids=[])
