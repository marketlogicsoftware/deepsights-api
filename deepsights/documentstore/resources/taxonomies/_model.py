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
This module contains Pydantic models for custom taxonomy entities.
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field

from deepsights.utils import DeepSightsBaseModel, DeepSightsIdModel


#################################################
class Origin(DeepSightsBaseModel):
    """
    Read-only origin metadata for taxonomy entities.

    Attributes:
        creator_user (Optional[str]): User who created the entity.
        creator_app (Optional[str]): Application that created the entity.
        creation_time (Optional[datetime]): Creation timestamp.
        modifier_user (Optional[str]): User who last modified the entity.
        modifier_app (Optional[str]): Application that last modified the entity.
        modification_time (Optional[datetime]): Last modification timestamp.
        sync_time (Optional[datetime]): Time of entity synchronization with search service.
    """

    creator_user: Optional[str] = Field(default=None, description="User who created the entity.")
    creator_app: Optional[str] = Field(default=None, description="Application that created the entity.")
    creation_time: Optional[datetime] = Field(default=None, description="Creation timestamp.")
    modifier_user: Optional[str] = Field(default=None, description="User who last modified the entity.")
    modifier_app: Optional[str] = Field(default=None, description="Application that last modified the entity.")
    modification_time: Optional[datetime] = Field(default=None, description="Last modification timestamp.")
    sync_time: Optional[datetime] = Field(default=None, description="Time of entity synchronization with search service.")


#################################################
class Translation(DeepSightsBaseModel):
    """
    Translation for a taxon.

    Attributes:
        id (Optional[str]): Unique identifier of the translation.
        translation (str): The translated text.
        language_code (str): Language code (e.g., 'en', 'de').
        origin (Optional[Origin]): Origin metadata.
    """

    id: Optional[str] = Field(default=None, description="Unique identifier of the translation.")
    translation: str = Field(description="The translated text.")
    language_code: str = Field(description="Language code (e.g., 'en', 'de').")
    origin: Optional[Origin] = Field(default=None, description="Origin metadata.")


#################################################
class TaxonType(DeepSightsIdModel):
    """
    Represents a taxon type within a taxonomy.

    Attributes:
        id (str): Unique identifier of the taxon type.
        name (str): Name of the taxon type.
        description (Optional[str]): Description of the taxon type.
        external_id (Optional[str]): External identifier.
        origin (Optional[Origin]): Origin metadata (read-only).
    """

    name: str = Field(description="Name of the taxon type.")
    description: Optional[str] = Field(default=None, description="Description of the taxon type.")
    external_id: Optional[str] = Field(default=None, description="External identifier.")
    origin: Optional[Origin] = Field(default=None, description="Origin metadata (read-only).")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.id}: {self.name}"


#################################################
class Taxon(DeepSightsIdModel):
    """
    Represents a taxon within a taxonomy.

    Attributes:
        id (str): Unique identifier of the taxon.
        name (str): Name of the taxon.
        description (Optional[str]): Description of the taxon.
        taxon_type_id (Optional[str]): ID of the associated taxon type.
        parent_ids (List[str]): IDs of parent taxons for hierarchical relationships.
        external_id (Optional[str]): External identifier.
        origin (Optional[Origin]): Origin metadata (read-only).
        icon_gcs_object_id (Optional[str]): GCS object ID for the taxon icon.
        image_gcs_object_id (Optional[str]): GCS object ID for the taxon image.
        translations (List[Translation]): Translations for the taxon.
    """

    name: str = Field(description="Name of the taxon.")
    description: Optional[str] = Field(default=None, description="Description of the taxon.")
    taxon_type_id: Optional[str] = Field(default=None, description="ID of the associated taxon type.")
    parent_ids: List[str] = Field(default_factory=list, description="IDs of parent taxons for hierarchical relationships.")
    parent_external_ids: List[str] = Field(default_factory=list, description="External IDs of parent taxons (for import).")
    external_id: Optional[str] = Field(default=None, description="External identifier.")
    origin: Optional[Origin] = Field(default=None, description="Origin metadata (read-only).")
    icon_gcs_object_id: Optional[str] = Field(default=None, description="GCS object ID for the taxon icon.")
    image_gcs_object_id: Optional[str] = Field(default=None, description="GCS object ID for the taxon image.")
    translations: List[Translation] = Field(default_factory=list, description="Translations for the taxon.")

    def __init__(self, **kwargs: Any) -> None:
        # Handle None values from API response by converting to empty lists
        if kwargs.get("parent_ids") is None:
            kwargs["parent_ids"] = []
        if kwargs.get("parent_external_ids") is None:
            kwargs["parent_external_ids"] = []
        if kwargs.get("translations") is None:
            kwargs["translations"] = []
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.id}: {self.name}"


#################################################
class TaxonomyStatus:
    """Constants for taxonomy status values."""

    READY = "READY"
    CREATED = "CREATED"
    SCHEDULED_FOR_APPLYING = "SCHEDULED_FOR_APPLYING"
    APPLYING = "APPLYING"
    FAILED_TO_APPLY = "FAILED_TO_APPLY"


#################################################
class Taxonomy(DeepSightsIdModel):
    """
    Represents a custom taxonomy.

    Attributes:
        id (str): Unique identifier of the taxonomy.
        name (str): Name of the taxonomy.
        external_id (Optional[str]): External identifier.
        origin (Optional[Origin]): Origin metadata (read-only).
        taxon_types (List[TaxonType]): List of taxon types in this taxonomy.
        taxons (List[Taxon]): List of taxons in this taxonomy.
        status (Optional[str]): Taxonomy status (READY, CREATED, APPLYING, etc.).
    """

    name: str = Field(description="Name of the taxonomy.")
    external_id: Optional[str] = Field(default=None, description="External identifier.")
    origin: Optional[Origin] = Field(default=None, description="Origin metadata (read-only).")
    taxon_types: List[TaxonType] = Field(default_factory=list, description="List of taxon types in this taxonomy.")
    taxons: List[Taxon] = Field(default_factory=list, description="List of taxons in this taxonomy.")
    status: Optional[str] = Field(default=None, description="Taxonomy status (READY, CREATED, APPLYING, etc.).")

    def __init__(self, **kwargs: Any) -> None:
        # Handle None values from API response by converting to empty lists
        if kwargs.get("taxon_types") is None:
            kwargs["taxon_types"] = []
        if kwargs.get("taxons") is None:
            kwargs["taxons"] = []
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.id}: {self.name}"
