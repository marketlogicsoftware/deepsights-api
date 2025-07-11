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
This module contains the model classes for documents.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import AliasChoices, Field

from deepsights.documentstore.resources.documents._cache import (
    get_document,
    get_document_page,
)
from deepsights.utils import (
    DeepSightsBaseModel,
    DeepSightsIdModel,
    DeepSightsIdTitleModel,
)


#################################################
class SortingOrder:
    """
    Represents the sorting order for documents.
    """

    ASCENDING = "ASC"
    DESCENDING = "DESC"


#################################################
class SortingField:
    """
    Represents the sorting field for documents.
    """

    TITLE = "title"
    PUBLICATION_DATE = "publication_date"
    CREATION_DATE = "origin.creation_time"


#################################################
class DocumentPage(DeepSightsIdModel):
    """
    Represents a document page.

    Attributes:

        page_number (Optional[int], optional): The number of the page.
        text (Optional[str]): The text content of the page (optional).
    """

    page_number: Optional[int] = Field(
        default=None, description="The number of the page (one-based)."
    )
    text: Optional[str] = Field(
        default=None, description="The text content of the page."
    )


#################################################
class Document(DeepSightsIdTitleModel):
    """
    Represents a document.

    Attributes:

        status (str, optional): The status of the document.
        source (str, optional): The source of the document.
        file_name (str, optional): The name of the file.
        file_size (int, optional): The size of the file.
        description (str, optional): The description of the document.
        publication_date (datetime, optional): The publication date of the document.
        creation_date (datetime, optional): The creation date of the document.§
        page_ids (List[str], optional): The list of page IDs in the document.
        number_of_pages (int, optional): The total number of pages in the document.
    """

    status: Optional[str] = Field(description="The processing status of the document.")
    source: Optional[str] = Field(
        alias="ai_generated_source",
        default="n/a",
        description="The human-readable source of the document.",
    )
    file_name: Optional[str] = Field(default=None, description="The name of the file.")
    file_size: Optional[int] = Field(
        default=None, description="The size of the file in bytes."
    )
    description: Optional[str] = Field(
        alias="summary", description="The human-readable summary of the document."
    )
    publication_date: Optional[datetime] = Field(
        alias="publication_date",
        default=None,
        description="The publication date of the document.",
    )
    creation_date: Optional[datetime] = Field(
        alias="creation_date",
        default=None,
        description="The creation date of the document.",
    )
    page_ids: List[str] = Field(
        default=None, description="The list of page IDs in the document."
    )
    number_of_pages: Optional[int] = Field(
        alias="total_pages",
        default=None,
        description="The total number of pages in the document.",
    )

    def __init__(self, **kwargs):
        kwargs["creation_date"] = kwargs["origin"]["creation_time"]
        kwargs["publication_date"] = kwargs["publication_data"]["publication_date"]
        super().__init__(**kwargs)

    @property
    def pages(self) -> List[DocumentPage]:
        return [get_document_page(page_id) for page_id in self.page_ids]


#################################################
class DocumentPageSearchResult(DeepSightsIdModel):
    """
    Represents a search result for a page.

    Attributes:

        document_id (str): The ID of the document.
        score (float): The score of the search result.
    """

    document_id: str = Field(
        description="The ID of the document to which the page belongs."
    )
    score: float = Field(description="The score of the search result.")

    @property
    def page_number(self) -> DocumentPage:
        page = get_document_page(self.id)
        return page.page_number if page else None

    @property
    def text(self) -> str:
        page = get_document_page(self.id)
        return page.text if page else None


#################################################
class DocumentSearchResult(DeepSightsIdModel):
    """
    Represents the search result for a document.

    Attributes:

        page_matches (List[DocumentPageSearchResult]): The search results for each page of the document.
        rank (Optional[int]): The overall rank of the document.
    """

    page_matches: List[DocumentPageSearchResult] = Field(
        default=[], description="The matching page search results for the document."
    )
    rank: Optional[int] = Field(
        default=None, description="The final rank of the item in the search results."
    )

    @property
    def document(self) -> Document:
        return get_document(self.id)

    @property
    def publication_date(self) -> datetime:
        document = self.document
        return document.publication_date if document else None

    #############################################
    def __repr__(self) -> str:
        if self.document is not None:
            return f"{self.__class__.__name__}@{self.id}: {self.document.title}"

        return super().__repr__()


#################################################
class HybridSearchPageReference(DeepSightsBaseModel):
    """
    Represents a page reference in hybrid search results.

    Attributes:
        id (str): The ID of the page.
        external_id (str): External ID of the artifact page.
        number (int): Page number.
        title (str): The title of the page.
        text (str): The text of the page.
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


#################################################
class HybridSearchResult(DeepSightsBaseModel):
    """
    Represents a hybrid search result for a document.

    Attributes:
        artifact_id (str): The ID of the artifact.
        artifact_title (str): The title of the artifact.
        artifact_summary (str): Summary of the artifact.
        artifact_source (str): Source of the artifact.
        artifact_publication_date (datetime): Publication date of the artifact.
        page_references (List[HybridSearchPageReference]): Page references.
    """

    artifact_id: str = Field(description="The ID of the artifact.")
    artifact_title: str = Field(description="The title of the artifact.")
    artifact_summary: Optional[str] = Field(description="Summary of the artifact.")
    artifact_source: Optional[str] = Field(description="Source of the artifact.")
    artifact_publication_date: Optional[datetime] = Field(
        description="Publication date of the artifact."
    )
    page_references: List[HybridSearchPageReference] = Field(
        description="Page references."
    )
