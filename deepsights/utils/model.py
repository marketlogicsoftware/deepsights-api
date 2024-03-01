# Copyright 2024 Market Logic Software AG. All Rights Reserved.
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
This module contains the base classes for all DeepSights models.
"""

from typing import Optional
from pydantic import BaseModel, Field, AliasChoices


#################################################
class DeepSightsBaseModel(BaseModel):
    """
    Represents the base model for all DeepSights models.
    """

    #############################################
    def schema_human(self) -> str:
        """
        Returns a simplified human-readable string representation of the model's schema.

        The schema includes the field names, types, and descriptions.

        Returns:

            str: The model's schema.
        """
        return "\n".join(
            [
                f"{field_name} ({field.annotation}): {field.description}"
                for field_name, field in self.__class__.model_fields.items()
            ]
        )

    #############################################
    def __str__(self) -> str:
        return self.__repr__()


#################################################
class DeepSightsIdModel(DeepSightsBaseModel):
    """
    Represents the base model for all DeepSights models with an id.

    Attributes:

        id (str): The ID of the item.
    """

    id: str = Field(
        validation_alias=AliasChoices(
            "id", "item_id", "artifact_id", "page_id", "document_id"
        ),
        description="The ID of the item.",
    )

    #############################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.id}"


#################################################
class DeepSightsIdTitleModel(DeepSightsIdModel):
    """
    Represents the base model for all DeepSights models with an id and title.

    Attributes:

        title (Optional[str]): The human-readable title of the item.
    """

    title: Optional[str] = Field(
        validation_alias=AliasChoices("ai_generated_title", "title"),
        description="The human-readable title of the item.",
    )

    #############################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.id}: {self.title}"
