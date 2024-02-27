from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, AliasChoices


class BaseAnswer(BaseModel):
    """
    Represents a base answer object.

    Attributes:
        id (str): The ID of the answer.
        artifact_id (str): The ID of the artifact.
        artifact_type (str): The type of the artifact.
        title (str, optional): The title of the answer. Defaults to None.
        summary (str): The summary of the answer.
        timestamp (datetime, optional): The publication date of the answer. Defaults to None.
    """

    id: str
    artifact_id: str
    artifact_type: str
    title: Optional[str] = Field(
        validation_alias=AliasChoices("ai_generated_title", "title")
    )
    summary: str
    timestamp: Optional[datetime] = Field(alias="publication_date", default=None)


class DocumentAnswerPageReference(BaseModel):
    """
    Represents a reference to a specific page in a document with a corresponding score.
    """

    page_id: str = Field(alias="id")
    page_number: int = Field(alias="number")
    score: float

    def __repr__(self) -> str:
        return f"DocumentAnswerPageReference@{self.page_id} - {self.score}"


class DocumentAnswer(BaseAnswer):
    """
    Represents an answer that is a document.

    Attributes:
        artifact_type (str): The type of the artifact, which is set to "DOCUMENT".
        pages (Optional[int]): The total number of pages in the document.
    """

    artifact_type: str = "DOCUMENT"
    pages: List[DocumentAnswerPageReference] = Field(alias="page_references")

    def __repr__(self) -> str:
        return f"DocumentAnswer@{self.id} - {self.title}"
