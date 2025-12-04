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
This module contains CRUD functions for custom taxonomies.
"""

from typing import List, Optional, Tuple

from deepsights.api import APIResource
from deepsights.documentstore.resources.taxonomies._model import Taxonomy

BASE_PATH = "/taxonomy-config-service"


#################################################
def taxonomy_create(
    resource: APIResource,
    name: str,
    external_id: Optional[str] = None,
) -> Taxonomy:
    """
    Create a new custom taxonomy.

    Args:
        resource (APIResource): An instance of the API resource.
        name (str): Name of the taxonomy.
        external_id (Optional[str]): Optional external identifier.

    Returns:
        Taxonomy: The created taxonomy.
    """
    assert name, "Taxonomy name is required."

    body: dict = {"name": name}
    if external_id:
        body["external_id"] = external_id

    result = resource.api.post(f"{BASE_PATH}/custom-taxonomies", body=body)
    return Taxonomy.model_validate(result)


#################################################
def taxonomy_update(
    resource: APIResource,
    taxonomy_id: str,
    name: str,
) -> None:
    """
    Update an existing taxonomy.

    Args:
        resource (APIResource): An instance of the API resource.
        taxonomy_id (str): ID of the taxonomy to update.
        name (str): New name for the taxonomy.

    Returns:
        None: The API returns 204 No Content on success.
    """
    assert taxonomy_id, "Taxonomy ID is required."
    assert name, "Taxonomy name is required."

    body = {"name": name}
    resource.api.put(f"{BASE_PATH}/custom-taxonomies/{taxonomy_id}", body=body)


#################################################
def taxonomy_delete(resource: APIResource, taxonomy_id: str) -> None:
    """
    Delete a taxonomy.

    Args:
        resource (APIResource): An instance of the API resource.
        taxonomy_id (str): ID of the taxonomy to delete.
    """
    assert taxonomy_id, "Taxonomy ID is required."
    resource.api.delete(f"{BASE_PATH}/custom-taxonomies/{taxonomy_id}")


#################################################
def taxonomy_search(
    resource: APIResource,
    ids: Optional[List[str]] = None,
    external_ids: Optional[List[str]] = None,
    include_taxons: bool = True,
    page_size: int = 10,
    page_number: int = 0,
) -> Tuple[int, List[Taxonomy]]:
    """
    Search for custom taxonomies.

    Args:
        resource (APIResource): An instance of the API resource.
        ids (Optional[List[str]]): List of taxonomy IDs to filter by.
        external_ids (Optional[List[str]]): List of external IDs to filter by.
        include_taxons (bool): Whether to include taxons in the response. Defaults to True.
        page_size (int): Number of results per page (max 100). Defaults to 10.
        page_number (int): Page number (0-indexed). Defaults to 0.

    Returns:
        Tuple[int, List[Taxonomy]]: Total count and list of matching taxonomies.
    """
    assert page_size <= 100, "Page size must be less than or equal to 100."
    assert page_size >= 1, "Page size must be at least 1."
    assert page_number >= 0, "Page number must be greater than or equal to 0."

    body: dict = {
        "size": page_size,
        "page": page_number,
        "include_taxons": include_taxons,
    }
    if ids:
        body["ids"] = ids
    if external_ids:
        body["external_ids"] = external_ids

    result = resource.api.post(f"{BASE_PATH}/custom-taxonomies/_search", body=body)

    total = result.get("total", 0)
    taxonomies = [Taxonomy.model_validate(item) for item in result.get("items", [])]
    return total, taxonomies
