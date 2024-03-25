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
This module contains the models for answers in the DeepSights API.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import Field, BaseModel, AliasChoices
from deepsights.utils import DeepSightsIdModel, DeepSightsIdTitleModel


#################################################
class BaseAnswer(DeepSightsIdTitleModel):
    """
    Represents a base answer object.

    Attributes:

        text (str): The summary of the answer.
        artifact_id (str): The ID of the artifact.
        artifact_type (str): The type of the artifact.
        artifact_description (Optional[str]): The human-readable summary of the artifact.
        publication_date (datetime, optional): The publication date of the answer. Defaults to None.
    """

    text: str = Field(
        alias="summary",
        description="The answer text generated based on the artifact.",
        default=None,
    )
    artifact_id: str = Field(
        description="The ID of the artifact from which the answer is derived."
    )
    artifact_type: str = Field(
        description="The type of the artifact from which the answer is derived."
    )
    artifact_description: Optional[str] = Field(
        alias="artifact_summary",
        default=None,
        description="The human-readable summary of the artifact.",
    )
    publication_date: Optional[datetime] = Field(
        alias="publication_date",
        default=None,
        description="The publication date of the artifact from which the answer is derived.",
    )


#################################################
class DocumentAnswerPageReference(DeepSightsIdModel):
    """
    Represents a reference to a specific page in a document.

    Attributes:

        page_number (int): The page number in the document.
    """

    page_number: int = Field(
        validation_alias=AliasChoices("page_number", "number"),
        description="The page number in the document.",
    )


#################################################
class DocumentAnswer(BaseAnswer):
    """
    Represents an answer that is a document.

    Attributes:

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


#################################################
class DocumentAnswerSet(BaseModel):
    """
    Represents an answer set that contains document answers.

    Attributes:

        answers (List[DocumentAnswer]): The list of document answers in the set.
        permission_validation (str): The permission validation of the answer set for the caller.
        search_results (List[DocumentAnswer]): The list of initial search results used to ground the answer.
    """
    permission_validation: str = Field(
        description="The permission validation of the answer set for the caller.",
    )

    answers: List[DocumentAnswer] = Field(
        description="The list of document answers in the set."
    )

    search_results: List[DocumentAnswer] = Field(   
        description="The list of initial search results used to ground the answer."
    )
