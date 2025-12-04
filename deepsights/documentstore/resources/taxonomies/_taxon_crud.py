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
This module contains CRUD functions for taxons.
"""

from typing import List, Optional, Tuple

from deepsights.api import APIResource
from deepsights.documentstore.resources.taxonomies._model import Taxon

BASE_PATH = "/taxonomy-config-service"


#################################################
# pylint: disable-next=too-many-arguments, too-many-positional-arguments
def taxon_create(
    resource: APIResource,
    taxonomy_id: str,
    taxon_type_id: str,
    name: str,
    description: Optional[str] = None,
    parent_ids: Optional[List[str]] = None,
    external_id: Optional[str] = None,
) -> Taxon:
    """
    Create a new taxon within a taxonomy.

    Args:
        resource (APIResource): An instance of the API resource.
        taxonomy_id (str): ID of the parent taxonomy.
        taxon_type_id (str): ID of the taxon type.
        name (str): Name of the taxon.
        description (Optional[str]): Description of the taxon.
        parent_ids (Optional[List[str]]): IDs of parent taxons for hierarchical relationships.
        external_id (Optional[str]): Optional external identifier.

    Returns:
        Taxon: The created taxon.
    """
    assert taxonomy_id, "Taxonomy ID is required."
    assert taxon_type_id, "Taxon type ID is required."
    assert name, "Taxon name is required."

    body: dict = {"name": name}
    if description:
        body["description"] = description
    if parent_ids:
        body["parent_ids"] = parent_ids
    if external_id:
        body["external_id"] = external_id

    result = resource.api.post(
        f"{BASE_PATH}/custom-taxonomies/{taxonomy_id}/taxon-types/{taxon_type_id}/taxons",
        body=body,
    )
    return Taxon.model_validate(result)


#################################################
# pylint: disable-next=too-many-arguments, too-many-positional-arguments
def taxon_update(
    resource: APIResource,
    taxon_id: str,
    taxon_type_id: str,
    name: str,
    description: Optional[str] = None,
) -> None:
    """
    Update an existing taxon.

    Args:
        resource (APIResource): An instance of the API resource.
        taxon_id (str): ID of the taxon to update.
        taxon_type_id (str): ID of the taxon type (required by API).
        name (str): New name for the taxon.
        description (Optional[str]): New description for the taxon.

    Returns:
        None: The API returns 204 No Content on success.
    """
    assert taxon_id, "Taxon ID is required."
    assert taxon_type_id, "Taxon type ID is required."
    assert name, "Taxon name is required."

    body: dict = {
        "name": name,
        "taxon_type_id": taxon_type_id,
    }
    if description is not None:
        body["description"] = description

    resource.api.put(f"{BASE_PATH}/custom-taxons/{taxon_id}", body=body)


#################################################
def taxon_delete(resource: APIResource, taxon_id: str) -> None:
    """
    Delete a taxon.

    Note: Taxons with children cannot be deleted. Delete children first.

    Args:
        resource (APIResource): An instance of the API resource.
        taxon_id (str): ID of the taxon to delete.

    Raises:
        HTTPError: If the taxon has children and cannot be deleted.
    """
    assert taxon_id, "Taxon ID is required."
    resource.api.delete(f"{BASE_PATH}/custom-taxons/{taxon_id}")


#################################################
def taxon_search(
    resource: APIResource,
    ids: Optional[List[str]] = None,
    external_ids: Optional[List[str]] = None,
    page_size: int = 10,
    page_number: int = 0,
) -> Tuple[int, List[Taxon]]:
    """
    Search for taxons.

    Args:
        resource (APIResource): An instance of the API resource.
        ids (Optional[List[str]]): List of taxon IDs to filter by.
        external_ids (Optional[List[str]]): List of external IDs to filter by.
        page_size (int): Number of results per page (max 100). Defaults to 10.
        page_number (int): Page number (0-indexed). Defaults to 0.

    Returns:
        Tuple[int, List[Taxon]]: Total count and list of matching taxons.
    """
    assert page_size <= 100, "Page size must be less than or equal to 100."
    assert page_size >= 1, "Page size must be at least 1."
    assert page_number >= 0, "Page number must be greater than or equal to 0."

    body: dict = {
        "size": page_size,
        "page": page_number,
    }
    if ids:
        body["ids"] = ids
    if external_ids:
        body["external_ids"] = external_ids

    result = resource.api.post(f"{BASE_PATH}/custom-taxonomies/_search-taxons", body=body)

    total = result.get("total", 0)
    # API returns items wrapped in {"taxon": {...}} structure
    items = result.get("items", [])
    taxons = [Taxon.model_validate(item.get("taxon", item)) for item in items]
    return total, taxons
