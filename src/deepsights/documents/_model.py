from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, AliasChoices


class DocumentPage(BaseModel):
    """
    Represents a document page.

    Attributes:
        id (str): The ID of the page.
        page_number (Optional[int], optional): The number of the page.
        text (Optional[str]): The text content of the page (optional).
    """

    id: str
    page_number: Optional[int] = None
    text: Optional[str] = None

    def __repr__(self) -> str:
        return f"DocumentPage@{self.id}"


class Document(BaseModel):
    """
    Represents a document.

    Attributes:
        id (str): The ID of the document.
        status (str, optional): The status of the document.
        title (str, optional): The title of the document.
        source (str, optional): The source of the document.
        file_name (str, optional): The name of the file.
        file_size (int, optional): The size of the file.
        description (str, optional): The description of the document.
        timestamp (datetime, optional): The timestamp of the document.
        page_ids (List[DocumentPage], optional): The list of page IDs in the document.
        number_of_pages (int, optional): The total number of pages in the document.
    """

    id: str
    status: Optional[str] = None
    title: Optional[str] = Field(
        validation_alias=AliasChoices("ai_generated_title", "title")
    )
    source: Optional[str] = Field(alias="ai_generated_source", default=None)
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = Field(alias="summary")
    timestamp: Optional[datetime] = Field(alias="publication_date", default=None)
    page_ids: List[DocumentPage] = None
    number_of_pages: Optional[int] = Field(alias="total_pages", default=None)

    def __repr__(self) -> str:
        return f"Document@{self.id} - {self.title}"


class DocumentPageSearchResult(BaseModel):
    """
    Represents a search result for a page.

    Attributes:
        document_id (str): The ID of the document.
        page_id (str): The ID of the page.
        page (Optional[DocumentPage]): The page object, referenced if loaded.
        score (float): The score of the search result.
    """

    document_id: str
    page_id: str
    page: Optional[DocumentPage] = None
    score: float

    def __repr__(self) -> str:
        return f"DocumentPageSearchResult@{self.page_id} - {self.score}"


class DocumentSearchResult(BaseModel):
    """
    Represents the search result for a document.

    Attributes:
        document_id (str): The ID of the document.
        document (Optional[Document]): The document object, referenced if loaded.
        pages (List[DocumentPageSearchResult]): The search results for each page of the document.
        score_rank (Optional[int]): The rank of the document based on the score.
        age_rank (Optional[int]): The rank of the document based on the age.
        rank (Optional[int]): The overall rank of the document.
    """

    document_id: str
    document: Optional[Document] = None
    timestamp: Optional[datetime] =  None
    pages: List[DocumentPageSearchResult] = []
    score_rank: Optional[int] = None
    age_rank: Optional[int] = None
    rank: Optional[int] = None

    @property
    def id(self) -> str:
        # to provide uniqueness in the search results, e.g. for re-ranking
        return self.document_id

    def __repr__(self) -> str:
        return f"DocumentSearchResult@{self.document_id} - {self.rank} - (score: {self.score_rank} / age: {self.age_rank})"
