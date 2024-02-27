from typing import List, Optional
from datetime import datetime
from pydantic import Field
from deepsights.utils import DeepSightsIdModel, DeepSightsIdTitleModel


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
        timestamp (datetime, optional): The timestamp of the document.
        page_ids (List[DocumentPage], optional): The list of page IDs in the document.
        number_of_pages (int, optional): The total number of pages in the document.
    """

    status: Optional[str] = Field(description="The processing status of the document.")
    source: Optional[str] = Field(
        default=None, description="The human-readable source of the document."
    )
    file_name: Optional[str] = Field(default=None, description="The name of the file.")
    file_size: Optional[int] = Field(
        default=None, description="The size of the file in bytes."
    )
    description: Optional[str] = Field(
        alias="summary", description="The human-readable summary of the document."
    )
    timestamp: Optional[datetime] = Field(
        alias="publication_date",
        default=None,
        description="The publication timestamp of the document.",
    )
    page_ids: List[DocumentPage] = Field(
        default=None, description="The list of page IDs in the document."
    )
    number_of_pages: Optional[int] = Field(
        alias="total_pages",
        default=None,
        description="The total number of pages in the document.",
    )


#################################################
class DocumentPageSearchResult(DeepSightsIdModel):
    """
    Represents a search result for a page.

    Attributes:
        document_id (str): The ID of the document.
        page (Optional[DocumentPage]): The page object, referenced if loaded.
        score (float): The score of the search result.
    """

    document_id: str = Field(
        description="The ID of the document to which the page belongs."
    )
    page: Optional[DocumentPage] = Field(
        default=None, description="The page object; None if not loaded."
    )
    score: float = Field(description="The score of the search result.")


#################################################
class DocumentSearchResult(DeepSightsIdModel):
    """
    Represents the search result for a document.

    Attributes:
        document (Optional[Document]): The document object, referenced if loaded.
        pages (List[DocumentPageSearchResult]): The search results for each page of the document.
        score_rank (Optional[int]): The rank of the document based on the score.
        age_rank (Optional[int]): The rank of the document based on the age.
        rank (Optional[int]): The overall rank of the document.
    """

    document: Optional[Document] = Field(
        default=None, description="The document object; only referenced if loaded."
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="The publication timestamp of the document."
    )
    pages: List[DocumentPageSearchResult] = Field(
        default=[], description="The matching page search results for the document."
    )
    rank: Optional[int] = Field(
        default=None, description="The final rank of the item in the search results."
    )
    score_rank: Optional[int] = Field(
        default=None, description="The rank of the item based on its score."
    )
    age_rank: Optional[int] = Field(
        default=None, description="The rank of the item based on its age; may be None."
    )
