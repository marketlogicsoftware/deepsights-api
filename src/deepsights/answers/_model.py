from typing import Optional, List
from datetime import datetime
from pydantic import Field
from deepsights.utils import DeepSightsIdModel, DeepSightsIdTitleModel


#################################################
class BaseAnswer(DeepSightsIdTitleModel):
    """
    Represents a base answer object.

    Attributes:
        artifact_id (str): The ID of the artifact.
        artifact_type (str): The type of the artifact.
        summary (str): The summary of the answer.
        timestamp (datetime, optional): The publication date of the answer. Defaults to None.
    """

    artifact_id: str = Field(
        description="The ID of the artifact from which the answer is derived."
    )
    artifact_type: str = Field(
        description="The type of the artifact from which the answer is derived."
    )
    answer: str = Field(alias="summary", description="The answer from the artifact.")
    timestamp: Optional[datetime] = Field(
        alias="publication_date",
        default=None,
        description="The publication date of the artifact from which the answer is derived.",
    )


#################################################
class DocumentAnswerPageReference(DeepSightsIdModel):
    """
    Represents a reference to a specific page in a document with a corresponding score.
    """

    page_number: int = Field(
        alias="number", description="The page number in the document."
    )
    score: float = Field(description="The score of the page in the document.")


#################################################
class DocumentAnswer(BaseAnswer):
    """
    Represents an answer that is a document.

    Attributes
        artifact_type (str): The type of the artifact, which is set to "DOCUMENT".
        pages (Optional[int]): The total number of pages in the document.
    """

    artifact_type: str = Field(
        default="DOCUMENT",
        description="The type of the artifact from which the answer is derived.",
    )
    pages: List[DocumentAnswerPageReference] = Field(
        alias="page_references",
        description="The references to the pages in the document.",
    )
