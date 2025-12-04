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
This module contains CRUD functions for taxon types.
"""

from typing import Optional

from deepsights.api import APIResource
from deepsights.documentstore.resources.taxonomies._model import TaxonType

BASE_PATH = "/taxonomy-config-service"


#################################################
def taxon_type_create(
    resource: APIResource,
    taxonomy_id: str,
    name: str,
    description: Optional[str] = None,
    external_id: Optional[str] = None,
) -> TaxonType:
    """
    Create a new taxon type within a taxonomy.

    Args:
        resource (APIResource): An instance of the API resource.
        taxonomy_id (str): ID of the parent taxonomy.
        name (str): Name of the taxon type.
        description (Optional[str]): Description of the taxon type.
        external_id (Optional[str]): Optional external identifier.

    Returns:
        TaxonType: The created taxon type.
    """
    assert taxonomy_id, "Taxonomy ID is required."
    assert name, "Taxon type name is required."

    body: dict = {"name": name}
    if description:
        body["description"] = description
    if external_id:
        body["external_id"] = external_id

    result = resource.api.post(
        f"{BASE_PATH}/custom-taxonomies/{taxonomy_id}/taxon-types",
        body=body,
    )
    return TaxonType.model_validate(result)


#################################################
def taxon_type_update(
    resource: APIResource,
    taxon_type_id: str,
    name: str,
    description: Optional[str] = None,
) -> None:
    """
    Update an existing taxon type.

    Args:
        resource (APIResource): An instance of the API resource.
        taxon_type_id (str): ID of the taxon type to update.
        name (str): New name for the taxon type.
        description (Optional[str]): New description for the taxon type.

    Returns:
        None: The API returns 204 No Content on success.
    """
    assert taxon_type_id, "Taxon type ID is required."
    assert name, "Taxon type name is required."

    body: dict = {"name": name}
    if description is not None:
        body["description"] = description

    resource.api.put(f"{BASE_PATH}/custom-taxon-types/{taxon_type_id}", body=body)


#################################################
def taxon_type_delete(resource: APIResource, taxon_type_id: str) -> None:
    """
    Delete a taxon type.

    Args:
        resource (APIResource): An instance of the API resource.
        taxon_type_id (str): ID of the taxon type to delete.
    """
    assert taxon_type_id, "Taxon type ID is required."
    resource.api.delete(f"{BASE_PATH}/custom-taxon-types/{taxon_type_id}")
