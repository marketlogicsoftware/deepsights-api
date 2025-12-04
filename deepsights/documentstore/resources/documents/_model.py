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
from typing import Any, Dict, List, Optional

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
        context (Optional[str]): The context of the page (optional).
    """

    page_number: Optional[int] = Field(default=None, description="The number of the page (one-based).")
    text: Optional[str] = Field(default=None, description="The text content of the page.")
    context: Optional[str] = Field(default=None, description="The context of the page.")


# Nested model for external_metadata
class ArtifactExternalMetadata(DeepSightsBaseModel):
    """External metadata for artifacts - matches OpenAPI spec ArtifactExternalMetadata"""

    external_id: Optional[str] = None
    external_type: Optional[str] = None
    import_batch_id: Optional[str] = None
    external_properties: Optional[Dict[str, str]] = None
    external_source_url: Optional[str] = None


#################################################
class DocumentTaxonomy(DeepSightsBaseModel):
    """
    Represents taxonomy data assigned to a document in search results.

    Attributes:
        taxonomy_id (str): The ID of the taxonomy.
        taxons (List[str]): List of taxon IDs assigned to this document.
    """

    taxonomy_id: str = Field(description="The ID of the taxonomy.")
    taxons: List[str] = Field(default_factory=list, description="List of taxon IDs assigned to this document.")

    def __init__(self, **kwargs: Any) -> None:
        # Handle null -> empty list for taxons from API
        if kwargs.get("taxons") is None:
            kwargs["taxons"] = []
        super().__init__(**kwargs)


#################################################
class DocumentTaxonomyData(DeepSightsBaseModel):
    """
    Represents detailed taxonomy data from document/artifact response.

    Attributes:
        taxonomy_id (str): The ID of the taxonomy.
        effective (List[str]): Effective taxon IDs (computed from all sources).
        externally_provided (List[str]): Taxon IDs provided externally/manually.
        externally_excluded (List[str]): Taxon IDs explicitly excluded.
        ai_provided (List[str]): Taxon IDs provided by AI classification.
    """

    taxonomy_id: str = Field(description="The ID of the taxonomy.")
    effective: List[str] = Field(default_factory=list, description="Effective taxon IDs.")
    externally_provided: List[str] = Field(default_factory=list, description="Taxon IDs provided externally/manually.")
    externally_excluded: List[str] = Field(default_factory=list, description="Taxon IDs explicitly excluded.")
    ai_provided: List[str] = Field(default_factory=list, description="Taxon IDs provided by AI classification.")

    def __init__(self, **kwargs: Any) -> None:
        # Handle null -> empty list for list fields from API
        if kwargs.get("effective") is None:
            kwargs["effective"] = []
        if kwargs.get("externally_provided") is None:
            kwargs["externally_provided"] = []
        if kwargs.get("externally_excluded") is None:
            kwargs["externally_excluded"] = []
        if kwargs.get("ai_provided") is None:
            kwargs["ai_provided"] = []
        super().__init__(**kwargs)


#################################################
class CustomTaxonomyUpdate(DeepSightsBaseModel):
    """
    Request model for updating taxonomy assignments on a document.

    Attributes:
        taxonomy_id (str): The ID of the taxonomy to update.
        provided_taxon_ids (List[str]): Taxon IDs to assign to the document.
        excluded_taxon_ids (List[str]): Taxon IDs to explicitly exclude.
    """

    taxonomy_id: str = Field(description="The ID of the taxonomy.")
    provided_taxon_ids: List[str] = Field(default_factory=list, description="Taxon IDs to assign.")
    excluded_taxon_ids: List[str] = Field(default_factory=list, description="Taxon IDs to exclude.")


#################################################
class TaxonomyFilter(DeepSightsBaseModel):
    """
    Filter for search requests to filter by taxonomy.

    Attributes:
        field (str): The taxonomy ID to filter by.
        values (List[str]): List of taxon IDs to match.
    """

    field: str = Field(description="The taxonomy ID to filter by.")
    values: List[str] = Field(default_factory=list, description="List of taxon IDs to match.")


#################################################
class Document(DeepSightsIdTitleModel):
    """
    Represents a document.

    Attributes:

        status (str, optional): The status of the document.
        source (str, optional): The source of the document.
        content_type (str, optional): The type of the document.
        file_name (str, optional): The name of the file.
        file_size (int, optional): The size of the file.
        description (str, optional): The description of the document.
        publication_date (datetime, optional): The publication date of the document.
        creation_date (datetime, optional): The creation date of the document.
        page_ids (List[str], optional): The list of page IDs in the document.
        number_of_pages (int, optional): The total number of pages in the document.
    """

    status: Optional[str] = Field(description="The processing status of the document.")
    source: Optional[str] = Field(
        alias="ai_generated_source",
        default="n/a",
        description="The human-readable source of the document.",
    )
    content_type: Optional[str] = Field(description="The type of the document.")
    file_name: Optional[str] = Field(default=None, description="The name of the file.")
    original_file_name: Optional[str] = Field(default=None, description="The original name of the file at ingestion.")
    file_size: Optional[int] = Field(default=None, description="The size of the file in bytes.")
    description: Optional[str] = Field(alias="summary", description="The human-readable summary of the document.")
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
    page_ids: List[str] = Field(default_factory=list, description="The list of page IDs in the document.")
    number_of_pages: Optional[int] = Field(
        alias="total_pages",
        default=None,
        description="The total number of pages in the document.",
    )
    file_type: Optional[str] = Field(
        description="The class of artifact [ORIGINAL_PDF, CONVERTIBLE_TO_PDF, NON_BINARY]", alias="type", default=None
    )
    external_metadata: Optional[ArtifactExternalMetadata] = Field(description="The artifact's metadata", default=None)
    custom_taxonomies_data: List[DocumentTaxonomyData] = Field(default_factory=list, description="Taxonomy assignments for this document.")

    def __init__(self, **kwargs: Any) -> None:
        # Defensive extraction: tolerate missing fields from upstream services
        origin: Dict[str, Any] = kwargs.get("origin") or {}
        publication_data: Dict[str, Any] = kwargs.get("publication_data") or {}
        kwargs.setdefault("creation_date", origin.get("creation_time"))
        kwargs.setdefault("publication_date", publication_data.get("publication_date"))
        # Handle null -> empty list for custom_taxonomies_data
        if kwargs.get("custom_taxonomies_data") is None:
            kwargs["custom_taxonomies_data"] = []
        super().__init__(**kwargs)

    @property
    def pages(self) -> List[DocumentPage]:
        """Return list of pages for this document from cache (may be empty)."""
        return [get_document_page(page_id) for page_id in self.page_ids]


#################################################
class DocumentPageSearchResult(DeepSightsIdModel):
    """
    Represents a search result for a page.

    Attributes:

        document_id (str): The ID of the document.
        score (float): The score of the search result.
    """

    document_id: str = Field(description="The ID of the document to which the page belongs.")
    score: float = Field(description="The score of the search result.")

    @property
    def page_number(self) -> Optional[int]:
        """Return page number for this search result if cached, else None."""
        page = get_document_page(self.id)
        return page.page_number if page else None

    @property
    def text(self) -> Optional[str]:
        """Return page text for this search result if cached, else None."""
        page = get_document_page(self.id)
        return page.text if page else None

    @property
    def context(self) -> Optional[str]:
        """Return page context for this search result if cached, else None."""
        page = get_document_page(self.id)
        return page.context if page else None


#################################################
class DocumentSearchResult(DeepSightsIdModel):
    """
    Represents the search result for a document.

    Attributes:

        page_matches (List[DocumentPageSearchResult]): The search results for each page of the document.
        rank (Optional[int]): The overall rank of the document.
    """

    page_matches: List[DocumentPageSearchResult] = Field(
        default_factory=list,
        description="The matching page search results for the document.",
    )
    rank: Optional[int] = Field(default=None, description="The final rank of the item in the search results.")

    @property
    def document(self) -> Optional[Document]:
        """Return the cached Document for this result id, if available."""
        return get_document(self.id)

    @property
    def publication_date(self) -> Optional[datetime]:
        """Return the document's publication date if available, else None."""
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
class TopicSearchPageReference(DeepSightsBaseModel):
    """
    Represents a page reference in topic search results.

    Attributes:
        id (str): The ID of the page.
        external_id (str): External ID of the artifact page.
        number (int): Page number.
        title (str): The title of the page.
        text (str): The text of the page.
        relevance_class (str): Relevance classification.
        relevance_assessment (str): Relevance assessment.
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
class HybridSearchResult(DeepSightsBaseModel):
    """
    Represents a hybrid search result for a document.

    Attributes:
        artifact_id (str): The ID of the artifact.
        artifact_title (str): The title of the artifact.
        artifact_summary (str): Summary of the artifact.
        artifact_source (str): Source of the artifact.
        artifact_content_type (str): Type of the artifact.
        artifact_publication_date (datetime): Publication date of the artifact.
        page_references (List[HybridSearchPageReference]): Page references.
    """

    artifact_id: str = Field(description="The ID of the artifact.")
    artifact_title: str = Field(description="The title of the artifact.")
    artifact_summary: Optional[str] = Field(description="Summary of the artifact.")
    artifact_source: Optional[str] = Field(description="Source of the artifact.")
    artifact_content_type: Optional[str] = Field(description="Type of the artifact.")
    artifact_publication_date: Optional[datetime] = Field(description="Publication date of the artifact.")
    page_references: List[HybridSearchPageReference] = Field(description="Page references.")
    custom_taxonomies: List[DocumentTaxonomy] = Field(default_factory=list, description="Taxonomy assignments for this document.")


#################################################
class TopicSearchResult(DeepSightsBaseModel):
    """
    Represents a topic search result for a document.

    Attributes:
        artifact_id (str): The ID of the artifact.
        artifact_title (str): The title of the artifact.
        artifact_summary (str): Summary of the artifact.
        artifact_source (str): Source of the artifact.
        artifact_content_type (str): Type of the artifact.
        artifact_publication_date (datetime): Publication date of the artifact.
        page_references (List[TopicSearchPageReference]): Page references.
        relevance_class (str): Relevance classification.
    """

    artifact_id: str = Field(description="The ID of the artifact.")
    artifact_title: str = Field(description="The title of the artifact.")
    artifact_summary: Optional[str] = Field(description="Summary of the artifact.")
    artifact_source: Optional[str] = Field(description="Source of the artifact.")
    artifact_content_type: Optional[str] = Field(description="Type of the artifact.")
    artifact_publication_date: Optional[datetime] = Field(description="Publication date of the artifact.")
    page_references: List[TopicSearchPageReference] = Field(description="Page references.")
    relevance_class: Optional[str] = Field(description="Relevance classification.")
    relevance_assessment: Optional[str] = Field(description="Reasoning for relevance class", default="")
    custom_taxonomies: List[DocumentTaxonomy] = Field(default_factory=list, description="Taxonomy assignments for this document.")
