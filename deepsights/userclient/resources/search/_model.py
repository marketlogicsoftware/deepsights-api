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
This module contains the model classes for topic search.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import AliasChoices, Field

from deepsights.utils import DeepSightsBaseModel


#################################################
class TopicSearchPageReference(DeepSightsBaseModel):
    """
    Represents a page reference in topic search results.

    Attributes:
        id (str): The ID of the page.
        external_id (str): External ID of the artifact page.
        number (int): Page number.
        title (str): The title of the page.
    """

    id: str = Field(
        description="The ID of the page.",
        validation_alias=AliasChoices("id", "page_id"),
    )
    external_id: Optional[str] = Field(
        description="External ID of the artifact page.",
        validation_alias=AliasChoices("external_id", "page_external_id"),
    )
    number: Optional[int] = Field(
        description="Page number.",
        validation_alias=AliasChoices("number", "page_number"),
    )
    title: Optional[str] = Field(
        description="The title of the page.",
        validation_alias=AliasChoices("title", "page_title"),
    )
    text: Optional[str] = Field(
        description="The text of the page.",
        validation_alias=AliasChoices("text", "page_text"),
    )
    relevance_class: Optional[str] = Field(description="Relevance classification.")
    relevance_assessment: Optional[str] = Field(description="Relevance assessment.")


#################################################
class TopicSearchResult(DeepSightsBaseModel):
    """
    Represents a topic search result for a document.

    Attributes:
        artifact_id (str): The ID of the artifact.
        artifact_title (str): The title of the artifact.
        artifact_summary (str): Summary of the artifact.
        artifact_source (str): Source of the artifact.
        artifact_publication_date (datetime): Publication date of the artifact.
        page_references (List[TopicSearchPageReference]): Page references.
        relevance_class (str): Relevance classification.
    """

    artifact_id: str = Field(description="The ID of the artifact.")
    artifact_title: str = Field(description="The title of the artifact.")
    artifact_summary: Optional[str] = Field(description="Summary of the artifact.")
    artifact_source: Optional[str] = Field(description="Source of the artifact.")
    artifact_publication_date: Optional[datetime] = Field(
        description="Publication date of the artifact."
    )
    page_references: List[TopicSearchPageReference] = Field(
        description="Page references."
    )
    relevance_class: Optional[str] = Field(description="Relevance classification.")